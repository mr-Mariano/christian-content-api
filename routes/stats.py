import json
import falcon
from db.cassandra import (
    get_activity_by_user, get_activity_by_user_filtered,
    get_daily_active_users, get_activity_by_content,
    get_content_stats
)
from db.mongo import get_system_stats


class ActivityResource:
    def on_get(self, req, resp, user_id):
        results = get_activity_by_user(user_id)
        resp.text = json.dumps({"activity": results})


class ActivityFilteredResource:
    def on_get(self, req, resp, user_id):
        action_type = req.get_param("type")
        results = get_activity_by_user_filtered(user_id, action_type)
        resp.text = json.dumps({"activity": results})


class DailyActiveUsersResource:
    def on_get(self, req, resp):
        date = req.get_param("date")
        results = get_daily_active_users(date)
        resp.text = json.dumps({"daily_active_users": results})


class ContentActivityResource:
    def on_get(self, req, resp, content_id):
        activity = get_activity_by_content(content_id)
        stats = get_content_stats(content_id)
        resp.text = json.dumps({
            "stats": stats,
            "activity": activity
        })


class SystemStatsResource:
    def on_get(self, req, resp):
        stats = get_system_stats()
        resp.text = json.dumps({"stats": stats})
