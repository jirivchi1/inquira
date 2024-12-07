from flask import Flask


def create_app():
    app = Flask(__name__)

    # Aquí puedes registrar blueprints, configuraciones, etc.
    from .routes import routes  # Importa el blueprint de las rutas

    app.register_blueprint(routes)  # Registra el blueprint en la aplicación

    return app
