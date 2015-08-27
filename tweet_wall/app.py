# -*- coding: utf-8 -*-
import os
import json
from flask import Flask, render_template
from .extensions import db
from . import model


def load_test_tweets_if_empty():
    if model.Tweet.objects.count() != 0:
        return

    with open('./twitter_mock.json') as f:
        tweet_data = json.load(f)

    for tweet in tweet_data["statuses"]:
        tweet.pop("id")
        tweet["approved"] = False
        model.Tweet(**tweet).save()


def twitter_normal_to_bigger(value):
    return value.replace("_normal.", ".")


def create_app(config=None):
    app = Flask("tweet_wall")

    app.config['MONGODB_DB'] = os.getenv('TW_MONGODB_DB')
    app.config['MONGODB_HOST'] = os.getenv('TW_MONGODB_HOST')

    db.init_app(app)

    app.jinja_env.filters['twitter_normal_to_bigger'] = twitter_normal_to_bigger

    load_test_tweets_if_empty()

    @app.route("/")
    def wall():
        tweets = model.Tweet.objects(approved=True).all()
        return render_template('layout.html', tweets=tweets)

    return app
