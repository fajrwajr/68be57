from flask import jsonify, request, g, abort

from api import api
from db.shared import db
from db.models.user import User
from db.models.user_post import UserPost
from db.models.post import Post
from db.utils import row_to_dict
from middlewares import auth_required
import json

@api.route("/posts", methods=["GET"])
# Getting All Posts from Post Model 
def get_all_posts():
    result = Post.query.all()
    if result == None:
        return jsonify({"error": "Invalid parameters"})
    return jsonify([data.toDict() for data in result]), 200


@api.route("/posts/<authorIds>", methods=["GET"])
# Getting Individual from Post Model using helper function
def get_posts(authorIds):
    result = Post.get_posts_by_user_id(authorIds)
    if result == None:
        return jsonify({"error": "Invalid parameters"})
    return jsonify([data.toDict() for data in result]), 200

@api.route("/posts/<postId>", methods=["PATCH"])
# @auth_required
def update_post(postId):
    post = Post.query.get(postId)
    #getting author_id and post_id and saving it to an empty object
    p = {}
    posts = Post.query.all()
    for post in posts:
        if not post.id in p:
            p[post.id] = []
        for user in post.users:
            p[post.id].append(user.id)
    text = request.json["text"]
    tags = request.json["tags"]

    post.text = text
    post.tags = tags
    out = {"authorIds": [*p.keys()], "tags": tags, "text": text}
    db.session.commit()
    return jsonify({"result": out})


@api.post("/posts")
@auth_required
def posts():
    # validation
    user = g.get("user")
    if user is None:
        return abort(401)

    data = request.get_json(force=True)
    text = data.get("text", None)
    tags = data.get("tags", None)
    if text is None:
        return jsonify({"error": "Must provide text for the new post"}), 400

    # Create new post
    post_values = {"text": text}
    if tags:
        post_values["tags"] = tags

    post = Post(**post_values)
    db.session.add(post)
    db.session.commit()

    user_post = UserPost(user_id=user.id, post_id=post.id)
    db.session.add(user_post)
    db.session.commit()

    return row_to_dict(post), 200
