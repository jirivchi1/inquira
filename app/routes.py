from flask import Blueprint, render_template
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
