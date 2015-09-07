# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template, redirect, url_for, request
from twitter import *

from .extensions import db
from . import model


def twitter_normal_to_bigger(value):
    return value.replace("_normal.", ".")


def _get_hash_tag_query_param():
    hash_tag = request.args.get("hash_tag")
    if hash_tag is None:
        hash_tag = "#emkval"

    return hash_tag


def create_app(config=None):
    app = Flask("tweet_wall")
    app.config['MONGODB_DB'] = os.getenv('TW_MONGODB_DB')
    app.config['MONGODB_HOST'] = os.getenv('TW_MONGODB_HOST')

    db.init_app(app)

    app.jinja_env.filters['twitter_normal_to_bigger'] = twitter_normal_to_bigger

    token = read_bearer_token_file(".oauth2_bearer_token")
    twitter = Twitter(auth=OAuth2(bearer_token=token))

    @app.route("/approved")
    def approved_tweets():
        tweets = model.Tweet.objects(approved=True).order_by("-id_str").all()
        return render_template('public.html', tweets=tweets)

    @app.route("/approve", methods=["GET"])
    def approve_tweet_get():
        hash_tag = _get_hash_tag_query_param()
        tweets_twitter = twitter.search.tweets(q=hash_tag)["statuses"]

        tweets_local = model.Tweet.objects(approved=True).all()
        tweets_local_ids = [tweet.id_str for tweet in tweets_local]

        tweets_not_approved = [tweet for tweet in tweets_twitter
                               if tweet["id_str"] not in tweets_local_ids]

        return render_template('approve_tweets.html',
                               tweets=tweets_not_approved)

    @app.route("/approve/<string:id_str>", methods=["POST"])
    def approve_tweet_post(id_str):
        tweet = twitter.statuses.show(id=id_str)
        tweet["approved"] = True
        tweet.pop("id")
        model.Tweet.objects(id_str=tweet["id_str"]).update_one(upsert=True,
                                                               **tweet)
        return redirect(url_for('approve_tweet_get'))

    @app.route("/twitter")
    def tweets():
        hash_tag = _get_hash_tag_query_param()
        tweet_search = twitter.search.tweets(q=hash_tag)["statuses"]
        return render_template('public.html', tweets=tweet_search)

    return app
