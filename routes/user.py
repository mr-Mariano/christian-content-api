import json
import falcon
from db.mongo import (
    update_user_field, add_preference,
    remove_preference, get_all_users, get_user_by_id
)


VALID_FIELDS = ["first_name", "last_name", "age", "location"]


class ListUsersResource:
    def on_get(self, req, resp):
        resp.text = json.dumps({"users": get_all_users()})


class UpdateUserResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        field = data.get("field")
        value = data.get("value")

        if not user_id or not field:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id and field required"})
            return

        if field not in VALID_FIELDS:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({
                "error": "invalid field",
                "valid_fields": VALID_FIELDS
            })
            return

        ok = update_user_field(user_id, field, value)
        if not ok:
            if not get_user_by_id(user_id):
                resp.status = falcon.HTTP_404
                resp.text = json.dumps({"error": "user not found"})
                return

            resp.status = falcon.HTTP_200
            resp.text = json.dumps({"message": "no change"})
            return

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({"message": "updated"})


class AddPreferenceResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        preference = data.get("preference")

        if not user_id or not preference:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id and preference required"})
            return

        ok = add_preference(user_id, preference)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({
            "message": "preference added" if ok else "no change (already exists)"
        })


class RemovePreferenceResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        preference = data.get("preference")

        if not user_id or not preference:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id and preference required"})
            return

        ok = remove_preference(user_id, preference)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({
            "message": "preference removed" if ok else "preference not found"
        })
