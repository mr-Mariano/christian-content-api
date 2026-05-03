import json
import os
import sys
import time

import requests


API = os.getenv("API_URL", "http://localhost:8000")
OUTPUT_FILE = "seed_results.json"


def wait_for_api():
    print("Waiting for API...")

    for i in range(40):
        try:
            r = requests.get(f"{API}/system-stats", timeout=5)
            if r.status_code == 200:
                print("API is ready")
                return
        except Exception:
            pass

        print(f"  attempt {i + 1}/40")
        time.sleep(3)

    print("Could not connect to API")
    sys.exit(1)


def post(path, payload):
    r = requests.post(f"{API}{path}", json=payload, timeout=30)

    if r.status_code >= 400:
        print(f"Request failed: POST {path}")
        print(json.dumps(payload, indent=2))
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text)
        sys.exit(1)

    return r.json()


def get(path, params=None):
    r = requests.get(f"{API}{path}", params=params, timeout=30)

    if r.status_code >= 400:
        print(f"Request failed: GET {path}")
        try:
            print(json.dumps(r.json(), indent=2))
        except Exception:
            print(r.text)
        sys.exit(1)

    return r.json()


def register_user(user):
    data = post("/register", user)
    return data["user_id"]


def login_user(email, password):
    data = post("/login", {"email": email, "password": password})
    return data["user_id"]


def main():
    wait_for_api()

    print("Resetting data...")
    post("/reset", {})

    users = {
        "admin": {
            "email": "admin@mail.com",
            "password": "123456",
            "preferences": ["prayer", "gratitude", "bible"],
            "first_name": "Ana",
            "last_name": "Rivera",
            "location": "Guadalajara",
            "role": "admin"
        },
        "alice": {
            "email": "alice@mail.com",
            "password": "123456",
            "preferences": ["anxiety", "sleep", "prayer"],
            "first_name": "Alice",
            "last_name": "Lopez",
            "location": "Guadalajara",
            "role": "user"
        },
        "bob": {
            "email": "bob@mail.com",
            "password": "123456",
            "preferences": ["community", "rosary", "forgiveness"],
            "first_name": "Bob",
            "last_name": "Martinez",
            "location": "Guadalajara",
            "role": "user"
        },
        "carla": {
            "email": "carla@mail.com",
            "password": "123456",
            "preferences": ["gratitude", "worship", "reflection"],
            "first_name": "Carla",
            "last_name": "Ramirez",
            "location": "Monterrey",
            "role": "user"
        },
        "diego": {
            "email": "diego@mail.com",
            "password": "123456",
            "preferences": ["bible", "prayer", "meditation"],
            "first_name": "Diego",
            "last_name": "Torres",
            "location": "Guadalajara",
            "role": "user"
        }
    }

    print("Creating users...")
    for name, user in users.items():
        users[name]["user_id"] = register_user(user)

    print("Logging users in once...")
    for user in users.values():
        login_user(user["email"], user["password"])

    print("Updating one profile to test sync...")
    post("/user/update", {
        "user_id": users["alice"]["user_id"],
        "field": "location",
        "value": "Zapopan"
    })

    print("Creating content...")
    contents = {
        "night_prayer": post("/content", {
            "user_id": users["admin"]["user_id"],
            "type": "prayer",
            "title": "Night Prayer for Peace",
            "body": "A short guided prayer for ending the day in peace, giving thanks for what went well and placing tomorrow in God's hands.",
            "tags": ["prayer", "sleep", "peace"]
        })["content_id"],
        "anxiety_prayer": post("/content", {
            "user_id": users["admin"]["user_id"],
            "type": "meditation",
            "title": "Guided Prayer for Anxiety Before an Exam",
            "body": "A calm prayer for moments of stress, focused on breathing, trust, and remembering that God's presence does not leave us in difficult moments.",
            "tags": ["anxiety", "prayer", "meditation"]
        })["content_id"],
        "gospel_reflection": post("/content", {
            "user_id": users["admin"]["user_id"],
            "type": "reflection",
            "title": "5 Minute Gospel Reflection on Matthew 11",
            "body": "A simple reflection on 'Come to me, all who are weary.' It is meant for students and young adults who need a pause during a busy day.",
            "tags": ["bible", "gospel", "reflection"]
        })["content_id"],
        "psalm_audio": post("/content", {
            "user_id": users["admin"]["user_id"],
            "type": "audio",
            "title": "Psalm 23 Audio Reflection",
            "body": "A short audio-style devotional based on Psalm 23, focused on rest, trust and God's guidance in everyday life.",
            "tags": ["psalm", "audio", "rest"]
        })["content_id"],
        "gratitude_journal": post("/content", {
            "user_id": users["admin"]["user_id"],
            "type": "article",
            "title": "3 Minute Gratitude Prayer",
            "body": "A simple practice of naming three blessings from the day and turning them into a short prayer of gratitude.",
            "tags": ["gratitude", "prayer", "daily"]
        })["content_id"]
    }

    print("Creating events...")
    events = {
        "prayer_night": post("/event", {
            "user_id": users["admin"]["user_id"],
            "title": "Young Adults Prayer Night",
            "location": "Guadalajara",
            "date": "2026-05-15",
            "category": "prayer"
        })["event_id"],
        "rosary_group": post("/event", {
            "user_id": users["admin"]["user_id"],
            "title": "Saturday Rosary Group",
            "location": "Guadalajara",
            "date": "2026-05-20",
            "category": "community"
        })["event_id"],
        "lectio_workshop": post("/event", {
            "user_id": users["admin"]["user_id"],
            "title": "Lectio Divina Workshop",
            "location": "Monterrey",
            "date": "2026-05-25",
            "category": "bible"
        })["event_id"]
    }

    print("Creating follows...")
    post("/follow", {
        "follower_id": users["alice"]["user_id"],
        "followee_id": users["bob"]["user_id"]
    })
    post("/follow", {
        "follower_id": users["bob"]["user_id"],
        "followee_id": users["diego"]["user_id"]
    })
    post("/follow", {
        "follower_id": users["carla"]["user_id"],
        "followee_id": users["alice"]["user_id"]
    })

    print("Creating likes, comments and shares...")
    post("/like", {
        "user_id": users["alice"]["user_id"],
        "content_id": contents["night_prayer"]
    })
    post("/like", {
        "user_id": users["bob"]["user_id"],
        "content_id": contents["gospel_reflection"]
    })
    post("/like", {
        "user_id": users["diego"]["user_id"],
        "content_id": contents["anxiety_prayer"]
    })

    post("/comment", {
        "user_id": users["alice"]["user_id"],
        "content_id": contents["anxiety_prayer"],
        "text": "I liked that this one feels short and calm. It fits well for stressful days."
    })
    post("/comment", {
        "user_id": users["bob"]["user_id"],
        "content_id": contents["gospel_reflection"],
        "text": "The Matthew 11 idea is good. It sounds natural and not too formal."
    })

    post("/share", {
        "from_user_id": users["alice"]["user_id"],
        "to_user_id": users["diego"]["user_id"],
        "content_id": contents["night_prayer"]
    })
    post("/share-external", {
        "user_id": users["bob"]["user_id"],
        "content_id": contents["gospel_reflection"],
        "platform": "whatsapp"
    })

    print("Creating notes...")
    note_1 = post("/notes", {
        "user_id": users["alice"]["user_id"],
        "title": "Favorite prayer",
        "text": "Try the night prayer again this week before sleeping."
    })["note_id"]
    note_2 = post("/notes", {
        "user_id": users["alice"]["user_id"],
        "title": "Verse to revisit",
        "text": "Read Matthew 11 again when I feel overwhelmed."
    })["note_id"]
    post("/notes/update", {
        "user_id": users["alice"]["user_id"],
        "note_id": note_1,
        "text": "Try the night prayer again this week and share it with Diego."
    })
    post(f"/notes/delete/{note_2}", {
        "user_id": users["alice"]["user_id"]
    })

    print("Creating event attendance...")
    post("/attend-event", {
        "user_id": users["bob"]["user_id"],
        "event_id": events["prayer_night"]
    })
    post("/attend-event", {
        "user_id": users["alice"]["user_id"],
        "event_id": events["rosary_group"]
    })
    post("/attend-event", {
        "user_id": users["carla"]["user_id"],
        "event_id": events["lectio_workshop"]
    })

    print("Creating one chatbot conversation...")
    post("/chatbot", {
        "user_id": users["alice"]["user_id"],
        "prompt": "Can you recommend something short to pray when I feel anxious at night?"
    })

    print("Running a few read queries...")
    get(f"/recommend/content/{users['alice']['user_id']}")
    get(f"/recommend/users/{users['alice']['user_id']}")
    get(f"/recommend/location/{users['alice']['user_id']}")
    get(f"/recommend/events/{users['alice']['user_id']}")
    get("/search-content", params={"query": "short prayer for anxiety"})
    get("/metrics/content")
    get("/trending")
    get("/dau")

    summary = {
        "api_url": API,
        "users": {
            name: {
                "user_id": user["user_id"],
                "email": user["email"],
                "password": user["password"],
                "role": user["role"]
            }
            for name, user in users.items()
        },
        "content": contents,
        "events": events,
        "notes": {
            "alice_note_kept": note_1
        }
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Seed completed. Summary saved to {OUTPUT_FILE}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
