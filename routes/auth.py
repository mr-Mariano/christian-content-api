import json
import falcon
from db.mongo import create_user, user_exists, check_password
from db.cassandra import log_activity


class RegisterResource:
    def on_post(self, req, resp):
        data = req.media

        email = data.get("email")
        password = data.get("password")
        preferences = data.get("preferences", [])

        if not email or not password:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "email and password required"})
            return

        if not preferences:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "at least one preference required"})
            return

        if user_exists(email):
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user already exists"})
            return

        if not isinstance(preferences, list):
            preferences = [preferences]

        user_data = {
            "email": email,
            "password": password,
            "preferences": preferences,
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "location": data.get("location", "Guadalajara"),
            "role": data.get("role", "user")
        }

        user_id = create_user(user_data)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({
            "user_id": user_id,
            "message": "user registered"
        })


class LoginResource:
    def on_post(self, req, resp):
        data = req.media
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "email and password required"})
            return

        user = check_password(email, password)

        if not user:
            resp.status = falcon.HTTP_401
            resp.text = json.dumps({"error": "invalid credentials"})
            return

        user_id = str(user["_id"])

        log_activity(user_id, "login", "")

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({
            "user_id": user_id,
            "email": user["email"],
            "role": user.get("role", "user"),
            "message": "login successful"
        })


class LogoutResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")

        if not user_id:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id required"})
            return

        log_activity(user_id, "logout", "")

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({"message": "logout successful"})
