import json
import falcon
from db.dgraph import follow_user, recommend_users, recommend_users_by_location
from db.cassandra import log_activity


class FollowResource:
    def on_post(self, req, resp):
        data = req.media
        follower_id = data.get("follower_id")
        followee_id = data.get("followee_id")

        if not follower_id or not followee_id:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "follower_id and followee_id required"})
            return

        ok, msg = follow_user(follower_id, followee_id)
        if not ok:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": msg})
            return

        log_activity(follower_id, "follow", followee_id)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"message": msg})


class RecommendUsersResource:
    def on_get(self, req, resp, user_id):
        results = recommend_users(user_id)
        resp.text = json.dumps({"recommendations": results})


class RecommendByLocationResource:
    def on_get(self, req, resp, user_id):
        results = recommend_users_by_location(user_id)
        resp.text = json.dumps({"recommendations": results})
