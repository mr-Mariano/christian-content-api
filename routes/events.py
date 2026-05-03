import json
import falcon
from db.mongo import create_event, get_events_by_location, get_all_events, is_admin
from db.dgraph import attend_event, get_user_events, recommend_events_by_connections
from db.cassandra import log_activity


class EventResource:
    def on_get(self, req, resp):
        resp.text = json.dumps({"events": get_all_events()})

    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")

        if not user_id or not is_admin(user_id):
            resp.status = falcon.HTTP_403
            resp.text = json.dumps({"error": "admin privileges required"})
            return

        event_data = {
            "title": data.get("title", ""),
            "location": data.get("location", ""),
            "date": data.get("date", ""),
            "category": data.get("category", "")
        }

        event_id = create_event(event_data)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"event_id": event_id})


class EventsByLocationResource:
    def on_get(self, req, resp):
        location = req.get_param("location")
        if not location:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "location required"})
            return

        events = get_events_by_location(location)
        resp.text = json.dumps({"events": events})


class AttendEventResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        event_id = data.get("event_id")

        if not user_id or not event_id:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id and event_id required"})
            return

        ok = attend_event(user_id, event_id)
        if not ok:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "already attending or invalid event"})
            return

        log_activity(user_id, "attend_event", event_id)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"message": "attending event"})


class UserEventsResource:
    def on_get(self, req, resp, user_id):
        events = get_user_events(user_id)
        resp.text = json.dumps({"events": events})


class RecommendEventsByConnectionsResource:
    def on_get(self, req, resp, user_id):
        events = recommend_events_by_connections(user_id)
        resp.text = json.dumps({"recommendations": events})
