import os
from flask import Flask
from .extensions import db
from .routes import main

# DATABASE_URL = os.environ.get('DATABASE_URL') 
DATABASE_URL = 'postgres://mynewpsql_user:gJuvm0l7QaVjUhjz8x6ayjgszrMFOQ13@dpg-cnll32q1hbls738r28k0-a.oregon-postgres.render.com/mynewpsql'

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    db.init_app(app)
    app.register_blueprint(main)
    return app


