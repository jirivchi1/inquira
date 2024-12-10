from .celery_app import celery
from flask import current_app
from datetime import datetime
import os
import requests
from pymongo import MongoClient
from openai import OpenAI


@celery.task()
def generate_image_task(prompt, username):
    # Limpiar espacios en blanco del username
    username = username.strip()

    # Obtener configuración desde current_app
    mongodb_uri = current_app.config["MONGODB_URI"]
    openai_api_key = current_app.config["OPENAI_API_KEY"]
    openai_api_key = current_app.config["OPENAI_API_KEY"]

    # Conectar a MongoDB
    mongo_client = MongoClient(mongodb_uri)
    db = mongo_client["image_generation"]
    questions_collection = db["questions"]

    # Configurar el cliente de OpenAI
    client = OpenAI(api_key=openai_api_key)

    # Crear el prompt final mezclando el texto base y el prompt del usuario
    system_prompt = f"eres un sistema experto que genera imagen de manera realista con la siguiente descripción: {prompt}"

    # Ruta a la imagen original que da contexto
    original_image_path = os.path.join(
        current_app.root_path, "static", "images", "original", "first.jpg"
    )

    # Llamada a la API para editar la imagen con contexto
    try:
        with open(original_image_path, "rb") as image_file:
            response = client.images.edit(
                image=image_file,
                prompt=system_prompt,
                n=1,
                size="1024x1024",
                response_format="url",
            )
    except Exception as e:
        # Manejar errores de la API
        questions_collection.update_one(
            {"user_name": username, "prompt": prompt},
            {"$set": {"status": "failed", "error": str(e)}},
        )
        return None

    # Extraer la URL de la imagen
    image_url = response.data[0].url

    # Descargar la imagen
    try:
        image_data = requests.get(image_url).content
    except Exception as e:
        # Manejar errores de descarga
        questions_collection.update_one(
            {"user_name": username, "prompt": prompt},
            {"$set": {"status": "failed", "error": "Failed to download image"}},
        )
        return None

    # Guardar la imagen en static/images/competition/
    image_filename = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    image_path = os.path.join(
        current_app.root_path, "static", "images", "competition", image_filename
    )
    with open(image_path, "wb") as file:
        file.write(image_data)

    # Actualizar el documento en MongoDB
    questions_collection.update_one(
        {"user_name": username, "prompt": prompt},
        {"$set": {"image_filename": image_filename, "status": "completed"}},
    )

    return image_filename
