import json
import falcon
from db.mongo import share_content, content_exists, get_user_by_id
from db.cassandra import log_activity


VALID_PLATFORMS = ["twitter", "facebook", "whatsapp", "instagram", "telegram"]


class ShareResource:
    def on_post(self, req, resp):
        data = req.media
        from_user_id = data.get("from_user_id")
        to_user_id = data.get("to_user_id")
        content_id = data.get("content_id")

        if not from_user_id or not to_user_id or not content_id:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "missing required fields"})
            return

        if not content_exists(content_id):
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"error": "content not found"})
            return

        if not get_user_by_id(to_user_id):
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"error": "target user not found"})
            return

        share_id = share_content(from_user_id, to_user_id, content_id, "internal")

        log_activity(from_user_id, "share_internal", content_id)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"share_id": share_id})


class ShareExternalResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        content_id = data.get("content_id")
        platform = data.get("platform")

        if not user_id or not content_id or not platform:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "missing required fields"})
            return

        if platform not in VALID_PLATFORMS:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({
                "error": "invalid platform",
                "valid_platforms": VALID_PLATFORMS
            })
            return

        if not content_exists(content_id):
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"error": "content not found"})
            return

        share_id = share_content(user_id, "", content_id, platform)

        log_activity(user_id, f"share_{platform}", content_id)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"share_id": share_id})
