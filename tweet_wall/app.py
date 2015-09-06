# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template, abort, redirect, url_for
from twitter import *

from .extensions import db
from . import model

HASH_TAG = "#emkvaldk"


def load_tweets(twitter_client):
    tweet_data = twitter_client.search.tweets(q=HASH_TAG)["statuses"]

    for tweet in tweet_data:
        tweet.pop("id")
        tweet["approved"] = False
        model.Tweet.objects(id_str=tweet["id_str"]).update_one(upsert=True,
                                                               **tweet)


def twitter_normal_to_bigger(value):
    return value.replace("_normal.", ".")


def create_app(config=None):
    app = Flask("tweet_wall")
    app.config['MONGODB_DB'] = os.getenv('TW_MONGODB_DB')
    app.config['MONGODB_HOST'] = os.getenv('TW_MONGODB_HOST')

    db.init_app(app)

    app.jinja_env.filters['twitter_normal_to_bigger'] = twitter_normal_to_bigger

    token = read_bearer_token_file(".oauth2_bearer_token")
    twitter = Twitter(auth=OAuth2(bearer_token=token))

    load_tweets(twitter)

    @app.route("/approved")
    def approved_tweets():
        tweets = model.Tweet.objects(approved=True).all()
        return render_template('public.html', tweets=tweets)

    @app.route("/approve", methods=["GET"])
    def approve_tweet_get():
        load_tweets(twitter)
        tweets = model.Tweet.objects(approved=False).order_by('id_str').all()
        return render_template('approve_tweets.html', tweets=tweets)

    @app.route("/approve/<string:id_str>", methods=["POST"])
    def approve_tweet_post(id_str):
        tweet = model.Tweet.objects.get(id_str=id_str) or abort(404)
        tweet.approved = True
        tweet.save()
        return redirect(url_for('approve_tweet_get'))

    @app.route("/twitter")
    def tweets():
        tweet_search = twitter.search.tweets(q=HASH_TAG)["statuses"]
        return render_template('public.html', tweets=tweet_search)

    return app
