import json
import falcon
from db.chroma import semantic_search


class SemanticSearchResource:
    def on_get(self, req, resp):
        query = req.get_param("query")
        if not query:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "query required"})
            return

        limit = int(req.get_param("limit") or 5)

        results = semantic_search(query, limit)

        resp.text = json.dumps({"results": results})
