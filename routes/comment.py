import json
import falcon
from db.mongo import (
    create_comment, get_comments_by_content,
    get_comments_by_user, content_exists
)
from db.cassandra import log_activity


class CommentResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        content_id = data.get("content_id")
        text = data.get("text")

        if not user_id or not content_id or not text:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id, content_id and text required"})
            return

        if not content_exists(content_id):
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"error": "content not found"})
            return

        comment_id = create_comment(user_id, content_id, text)

        log_activity(user_id, "comment", content_id)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"comment_id": comment_id})


class GetCommentsResource:
    def on_get(self, req, resp, content_id):
        comments = get_comments_by_content(content_id)
        resp.text = json.dumps({"comments": comments})


class GetCommentsByUserResource:
    def on_get(self, req, resp, user_id):
        comments = get_comments_by_user(user_id)
        resp.text = json.dumps({"comments": comments})
