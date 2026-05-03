import json
import falcon
from db.mongo import like_content, content_exists
from db.cassandra import log_activity


class LikeResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        content_id = data.get("content_id")

        if not user_id or not content_id:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id and content_id required"})
            return

        if not content_exists(content_id):
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"error": "content not found"})
            return

        like_id = like_content(user_id, content_id)

        if like_id is None:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "already liked"})
            return

        log_activity(user_id, "like", content_id)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"like_id": like_id})
