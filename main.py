from flask import Flask, render_template, request, session, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from applications.database import db

import os

def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "secret"
    
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

from applications.controllers import *

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=7777, debug=True)
