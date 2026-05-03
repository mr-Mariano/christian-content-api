import json
import falcon
from db.mongo import (
    create_content, recommend_content, get_content_metrics,
    get_trending_content, is_admin, get_all_content
)
from db.chroma import add_content_embedding


class ContentResource:
    def on_get(self, req, resp):
        resp.text = json.dumps({"content": get_all_content()})

    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")

        if not user_id or not is_admin(user_id):
            resp.status = falcon.HTTP_403
            resp.text = json.dumps({"error": "admin privileges required"})
            return

        content_data = {
            "type": data.get("type", "text"),
            "title": data.get("title", ""),
            "body": data.get("body", ""),
            "tags": data.get("tags", []),
            "created_by": user_id
        }

        content_id = create_content(content_data)

        # also add to chroma so semantic search works
        try:
            add_content_embedding(
                content_id,
                content_data["title"],
                content_data["body"],
                content_data["tags"]
            )
        except Exception as e:
            print(f"⚠️  Could not add embedding: {e}")

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"content_id": content_id})


class RecommendContentResource:
    def on_get(self, req, resp, user_id):
        results = recommend_content(user_id)
        resp.text = json.dumps({"recommendations": results})


class ContentMetricsResource:
    def on_get(self, req, resp):
        results = get_content_metrics()
        resp.text = json.dumps({"metrics": results})


class TrendingContentResource:
    def on_get(self, req, resp):
        results = get_trending_content()
        resp.text = json.dumps({"trending": results})
