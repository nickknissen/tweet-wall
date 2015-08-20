# -*- coding: utf-8 -*-
import os
from flask import Flask
from flask_mongoengine import MongoEngine

db = MongoEngine()


def create_app(config=None):
    app = Flask("tweet_wall")

    app.config['MONGODB_DB'] = os.getenv('TW_MONGODB_DB')
    app.config['MONGODB_HOST'] = os.getenv('TW_MONGODB_HOST')

    db.init_app(app)

    @app.route("/")
    def hello():
        return app.config
    return app
