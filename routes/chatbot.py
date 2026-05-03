import json
import falcon
from db.chroma import retrieve_for_rag
from db.mongo import save_conversation, get_conversations


def build_response(prompt, retrieved):
    """simple template-based RAG response. no external LLM needed."""
    if not retrieved:
        return (
            "I couldn't find specific content related to your question, "
            "but I'm here to help. Could you give me more details?"
        )

    parts = ["Based on what I found, here are some thoughts on your question:\n"]

    for r in retrieved:
        parts.append(f"\n• {r['title']}")

        text = r.get("text", "").strip()
        if text:
            snippet = text[:200].replace("\n", " ").strip()
            parts.append(f"  {snippet}...")

    parts.append("\n\nI hope this helps. Feel free to ask for more details.")
    return "\n".join(parts)


class ChatbotResource:
    def on_post(self, req, resp):
        data = req.media
        user_id = data.get("user_id")
        prompt = data.get("prompt")

        if not user_id or not prompt:
            resp.status = falcon.HTTP_400
            resp.text = json.dumps({"error": "user_id and prompt required"})
            return

        retrieved = retrieve_for_rag(prompt, limit=3)
        response_text = build_response(prompt, retrieved)

        save_conversation(user_id, prompt, response_text)

        resp.status = falcon.HTTP_200
        resp.text = json.dumps({
            "response": response_text,
            "sources": [
                {"content_id": r["content_id"], "title": r["title"]}
                for r in retrieved
            ]
        })


class ConversationsResource:
    def on_get(self, req, resp, user_id):
        convs = get_conversations(user_id)
        resp.text = json.dumps({"conversations": convs})
