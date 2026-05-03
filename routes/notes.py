import json
import falcon
from db.mongo import create_note, get_notes, update_note, delete_note


class NotesResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        text = data.get("text")
        title = data.get("title", "")

        if not user_id or not text:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id and text required"})
            return

        note_id = create_note(user_id, text, title)

        resp.status = falcon.HTTP_201
        resp.text = json.dumps({"note_id": note_id})

    def on_get(self, req, resp, user_id=None):
        if not user_id:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id required in URL"})
            return

        notes = get_notes(user_id)
        resp.text = json.dumps({"notes": notes})


class UpdateNoteResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        note_id = data.get("note_id")
        text = data.get("text")

        if not user_id or not note_id or not text:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "missing required fields"})
            return

        ok = update_note(note_id, user_id, text)
        if not ok:
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"error": "note not found or not owned"})
            return

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({"message": "note updated"})


class DeleteNoteResource:
    def on_post(self, req, resp, note_id):
        data = req.media
        user_id = data.get("user_id")

        if not user_id:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id required"})
            return

        ok = delete_note(note_id, user_id)
        if not ok:
            resp.status = falcon.HTTP_404
            resp.text = json.dumps({"error": "note not found or not owned"})
            return

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({"message": "note deleted"})
