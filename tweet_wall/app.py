# -*- coding: utf-8 -*-
import os
import json
from flask import Flask
from .extensions import db
from . import model


def load_test_tweets_if_empty():
    if model.Tweet.objects.count() != 0:
        return

    with open('./twitter_mock.json') as f:
        tweet_data = json.load(f)

    for tweet in tweet_data["statuses"]:
        tweet.pop("id")
        model.Tweet(**tweet).save()


def create_app(config=None):
    app = Flask("tweet_wall")

    app.config['MONGODB_DB'] = os.getenv('TW_MONGODB_DB')
    app.config['MONGODB_HOST'] = os.getenv('TW_MONGODB_HOST')

    db.init_app(app)

    load_test_tweets_if_empty()

    @app.route("/")
    def hello():
        tweets = model.Tweet.objects.only("text").all().to_json()
        return "<pre>" + tweets + "</pre>"
    return app
