from flask import Blueprint, render_template, request, redirect, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Conectar a MongoDB
mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["image_generation"]
questions_collection = db["questions"]

# Definir el blueprint para las rutas
routes = Blueprint("routes", __name__)


@routes.route("/")
def home():
    images = list(questions_collection.find({"category": "inicio"}))
    return render_template("index.html", images=images)


@routes.route("/competition")
def competition():
    images = list(questions_collection.find({"category": "competition"}))
    return render_template("competition.html", images=images)


@routes.route("/gallery")
def gallery():
    images = list(questions_collection.find({"category": "gallery"}))
    return render_template("gallery.html", images=images)


@routes.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        user_name = request.form.get("user_name")
        prompt = request.form.get("prompt")

        # Insertar en la base de datos con la misma estructura usada anteriormente
        question = {
            "user_name": user_name,
            "image_path": "images/original/first.jpg",
            "prompt": prompt,
            "category": "competition",
        }
        questions_collection.insert_one(question)

        # Redirigir a /competition para ver el nuevo dato
        return redirect(url_for("routes.competition"))

    # Si es GET, mostramos el formulario
    return render_template("submit.html")
