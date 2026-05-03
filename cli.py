import argparse
import requests
import json
import os
import sys

API = os.getenv("API_URL", "http://localhost:8000")
SESSION_FILE = "session.json"


def save_session(user_id, email, role):
    with open(SESSION_FILE, "w") as f:
        json.dump({"user_id": user_id, "email": email, "role": role}, f)


def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE) as f:
        return json.load(f)


def clear_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def require_session():
    s = load_session()
    if not s:
        print("❌ You must login first")
        sys.exit(1)
    return s


def pretty(r):
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except:
        print(r.text)


# ---------- auth ----------

def cmd_register(args):
    payload = {
        "email": args.email,
        "password": args.password,
        "preferences": args.preferences,
        "first_name": args.first_name or "",
        "last_name": args.last_name or "",
        "location": args.location or "Guadalajara",
        "role": args.role or "user"
    }
    r = requests.post(f"{API}/register", json=payload)
    pretty(r)


def cmd_login(args):
    r = requests.post(f"{API}/login", json={
        "email": args.email,
        "password": args.password
    })
    if r.status_code == 200:
        data = r.json()
        save_session(data["user_id"], data["email"], data.get("role", "user"))
        print(f"✅ logged in as {data['email']} ({data['user_id']})")
    else:
        pretty(r)


def cmd_logout(args):
    s = load_session()
    if not s:
        print("not logged in")
        return
    requests.post(f"{API}/logout", json={"user_id": s["user_id"]})
    clear_session()
    print("👋 logged out")


def cmd_whoami(args):
    s = load_session()
    if not s:
        print("not logged in")
    else:
        print(json.dumps(s, indent=2))


# ---------- user ----------

def cmd_update_user(args):
    s = require_session()
    r = requests.post(f"{API}/user/update", json={
        "user_id": s["user_id"],
        "field": args.field,
        "value": args.value
    })
    pretty(r)


def cmd_add_preference(args):
    s = require_session()
    r = requests.post(f"{API}/user/add-preference", json={
        "user_id": s["user_id"],
        "preference": args.preference
    })
    pretty(r)


def cmd_remove_preference(args):
    s = require_session()
    r = requests.post(f"{API}/user/remove-preference", json={
        "user_id": s["user_id"],
        "preference": args.preference
    })
    pretty(r)


def cmd_list_users(args):
    r = requests.get(f"{API}/users")
    pretty(r)


# ---------- content ----------

def cmd_create_content(args):
    s = require_session()
    r = requests.post(f"{API}/content", json={
        "user_id": s["user_id"],
        "type": args.type,
        "title": args.title,
        "body": args.body,
        "tags": args.tags or []
    })
    pretty(r)


def cmd_recommend_content(args):
    s = require_session()
    r = requests.get(f"{API}/recommend/content/{s['user_id']}")
    pretty(r)


def cmd_like_content(args):
    s = require_session()
    r = requests.post(f"{API}/like", json={
        "user_id": s["user_id"],
        "content_id": args.id
    })
    pretty(r)


def cmd_list_content(args):
    r = requests.get(f"{API}/content")
    pretty(r)


# ---------- comments ----------

def cmd_comment(args):
    s = require_session()
    r = requests.post(f"{API}/comment", json={
        "user_id": s["user_id"],
        "content_id": args.content_id,
        "text": args.text
    })
    pretty(r)


def cmd_comments_by_content(args):
    r = requests.get(f"{API}/comments/{args.content_id}")
    pretty(r)


def cmd_comments_by_user(args):
    s = require_session()
    r = requests.get(f"{API}/comments/user/{s['user_id']}")
    pretty(r)


# ---------- follow ----------

def cmd_follow(args):
    s = require_session()
    r = requests.post(f"{API}/follow", json={
        "follower_id": s["user_id"],
        "followee_id": args.user_id
    })
    pretty(r)


def cmd_recommend_users(args):
    s = require_session()
    r = requests.get(f"{API}/recommend/users/{s['user_id']}")
    pretty(r)


def cmd_recommend_users_by_location(args):
    s = require_session()
    r = requests.get(f"{API}/recommend/location/{s['user_id']}")
    pretty(r)


# ---------- share ----------

def cmd_share(args):
    s = require_session()
    r = requests.post(f"{API}/share", json={
        "from_user_id": s["user_id"],
        "to_user_id": args.user_id,
        "content_id": args.content_id
    })
    pretty(r)


def cmd_share_external(args):
    s = require_session()
    r = requests.post(f"{API}/share-external", json={
        "user_id": s["user_id"],
        "content_id": args.content_id,
        "platform": args.platform
    })
    pretty(r)


# ---------- activity ----------

def cmd_activity(args):
    s = require_session()
    params = {}
    if args.type:
        params["type"] = args.type
    r = requests.get(f"{API}/activity-filter/{s['user_id']}", params=params)
    pretty(r)


def cmd_dau(args):
    params = {}
    if args.date:
        params["date"] = args.date
    r = requests.get(f"{API}/dau", params=params)
    pretty(r)


# ---------- notes ----------

def cmd_create_note(args):
    s = require_session()
    r = requests.post(f"{API}/notes", json={
        "user_id": s["user_id"],
        "title": args.title or "",
        "text": args.text
    })
    pretty(r)


def cmd_get_notes(args):
    s = require_session()
    r = requests.get(f"{API}/notes/{s['user_id']}")
    pretty(r)


def cmd_update_note(args):
    s = require_session()
    r = requests.post(f"{API}/notes/update", json={
        "user_id": s["user_id"],
        "note_id": args.id,
        "text": args.text
    })
    pretty(r)


def cmd_delete_note(args):
    s = require_session()
    r = requests.post(f"{API}/notes/delete/{args.id}", json={
        "user_id": s["user_id"]
    })
    pretty(r)


# ---------- events ----------

def cmd_create_event(args):
    s = require_session()
    r = requests.post(f"{API}/event", json={
        "user_id": s["user_id"],
        "title": args.title,
        "location": args.location,
        "date": args.date,
        "category": args.category or ""
    })
    pretty(r)


def cmd_get_local_events(args):
    r = requests.get(f"{API}/events", params={"location": args.location})
    pretty(r)


def cmd_attend_event(args):
    s = require_session()
    r = requests.post(f"{API}/attend-event", json={
        "user_id": s["user_id"],
        "event_id": args.event_id
    })
    pretty(r)


def cmd_my_events(args):
    s = require_session()
    r = requests.get(f"{API}/my-events/{s['user_id']}")
    pretty(r)


def cmd_recommend_events(args):
    s = require_session()
    r = requests.get(f"{API}/recommend/events/{s['user_id']}")
    pretty(r)


def cmd_list_events(args):
    r = requests.get(f"{API}/event")
    pretty(r)


# ---------- chatbot / search ----------

def cmd_chatbot(args):
    s = require_session()
    r = requests.post(f"{API}/chatbot", json={
        "user_id": s["user_id"],
        "prompt": args.prompt
    })
    pretty(r)


def cmd_conversations(args):
    s = require_session()
    r = requests.get(f"{API}/conversations/{s['user_id']}")
    pretty(r)


def cmd_search(args):
    r = requests.get(f"{API}/search-content", params={"query": args.query})
    pretty(r)


# ---------- stats ----------

def cmd_metrics_content(args):
    r = requests.get(f"{API}/metrics/content")
    pretty(r)


def cmd_content_stats(args):
    r = requests.get(f"{API}/metrics/content/{args.content_id}")
    pretty(r)


def cmd_system_stats(args):
    r = requests.get(f"{API}/system-stats")
    pretty(r)


def cmd_trending(args):
    r = requests.get(f"{API}/trending")
    pretty(r)


# ---------- admin ----------

def cmd_reset(args):
    r = requests.post(f"{API}/reset")
    pretty(r)
    clear_session()


# ---------- argparse ----------

def build_parser():
    parser = argparse.ArgumentParser(description="Project CLI")
    sub = parser.add_subparsers(dest="command")

    # auth
    p = sub.add_parser("register")
    p.add_argument("--email", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--preferences", nargs="+", required=True)
    p.add_argument("--first-name", dest="first_name")
    p.add_argument("--last-name", dest="last_name")
    p.add_argument("--location")
    p.add_argument("--role")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("login")
    p.add_argument("--email", required=True)
    p.add_argument("--password", required=True)
    p.set_defaults(func=cmd_login)

    p = sub.add_parser("logout")
    p.set_defaults(func=cmd_logout)

    p = sub.add_parser("whoami")
    p.set_defaults(func=cmd_whoami)

    # user
    p = sub.add_parser("update-user")
    p.add_argument("--field", required=True)
    p.add_argument("--value", required=True)
    p.set_defaults(func=cmd_update_user)

    p = sub.add_parser("add-preference")
    p.add_argument("--preference", required=True)
    p.set_defaults(func=cmd_add_preference)

    p = sub.add_parser("remove-preference")
    p.add_argument("--preference", required=True)
    p.set_defaults(func=cmd_remove_preference)

    p = sub.add_parser("list-users")
    p.set_defaults(func=cmd_list_users)

    # content
    p = sub.add_parser("create-content")
    p.add_argument("--type", default="text")
    p.add_argument("--title", required=True)
    p.add_argument("--body", default="")
    p.add_argument("--tags", nargs="*")
    p.set_defaults(func=cmd_create_content)

    p = sub.add_parser("recommend-content")
    p.set_defaults(func=cmd_recommend_content)

    p = sub.add_parser("like-content")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_like_content)

    p = sub.add_parser("list-content")
    p.set_defaults(func=cmd_list_content)

    # comments
    p = sub.add_parser("comment")
    p.add_argument("--content-id", dest="content_id", required=True)
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_comment)

    p = sub.add_parser("comments-by-content")
    p.add_argument("--content-id", dest="content_id", required=True)
    p.set_defaults(func=cmd_comments_by_content)

    p = sub.add_parser("comments-by-user")
    p.set_defaults(func=cmd_comments_by_user)

    # follow
    p = sub.add_parser("follow-user")
    p.add_argument("--user-id", dest="user_id", required=True)
    p.set_defaults(func=cmd_follow)

    p = sub.add_parser("recommend-users")
    p.set_defaults(func=cmd_recommend_users)

    p = sub.add_parser("recommend-users-by-location")
    p.set_defaults(func=cmd_recommend_users_by_location)

    # share
    p = sub.add_parser("share-content")
    p.add_argument("--content-id", dest="content_id", required=True)
    p.add_argument("--user-id", dest="user_id", required=True)
    p.set_defaults(func=cmd_share)

    p = sub.add_parser("share-external")
    p.add_argument("--content-id", dest="content_id", required=True)
    p.add_argument("--platform", required=True)
    p.set_defaults(func=cmd_share_external)

    # activity
    p = sub.add_parser("get-activity-history")
    p.add_argument("--type")
    p.set_defaults(func=cmd_activity)

    p = sub.add_parser("get-daily-active-users")
    p.add_argument("--date")
    p.set_defaults(func=cmd_dau)

    # notes
    p = sub.add_parser("create-note")
    p.add_argument("--title")
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_create_note)

    p = sub.add_parser("get-notes")
    p.set_defaults(func=cmd_get_notes)

    p = sub.add_parser("update-note")
    p.add_argument("--id", required=True)
    p.add_argument("--text", required=True)
    p.set_defaults(func=cmd_update_note)

    p = sub.add_parser("delete-note")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_delete_note)

    # events
    p = sub.add_parser("create-event")
    p.add_argument("--title", required=True)
    p.add_argument("--location", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--category")
    p.set_defaults(func=cmd_create_event)

    p = sub.add_parser("get-local-events")
    p.add_argument("--location", required=True)
    p.set_defaults(func=cmd_get_local_events)

    p = sub.add_parser("attend-event")
    p.add_argument("--event-id", dest="event_id", required=True)
    p.set_defaults(func=cmd_attend_event)

    p = sub.add_parser("my-events")
    p.set_defaults(func=cmd_my_events)

    p = sub.add_parser("recommend-events-by-connections")
    p.set_defaults(func=cmd_recommend_events)

    p = sub.add_parser("list-events")
    p.set_defaults(func=cmd_list_events)

    # chatbot / search
    p = sub.add_parser("chatbot")
    p.add_argument("--prompt", required=True)
    p.set_defaults(func=cmd_chatbot)

    p = sub.add_parser("conversations")
    p.set_defaults(func=cmd_conversations)

    p = sub.add_parser("search-content")
    p.add_argument("--query", required=True)
    p.set_defaults(func=cmd_search)

    # stats
    p = sub.add_parser("stats-by-content")
    p.add_argument("--content-id", dest="content_id", required=True)
    p.set_defaults(func=cmd_content_stats)

    p = sub.add_parser("metrics-content")
    p.set_defaults(func=cmd_metrics_content)

    p = sub.add_parser("get-system-stats")
    p.set_defaults(func=cmd_system_stats)

    p = sub.add_parser("trending-content")
    p.set_defaults(func=cmd_trending)

    # admin
    p = sub.add_parser("reset")
    p.set_defaults(func=cmd_reset)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
