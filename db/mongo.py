from pymongo import MongoClient
from datetime import datetime, timezone
from bson import ObjectId
import hashlib
from db.dgraph import create_user_node, create_event_node, update_user_location


client = MongoClient("mongodb://localhost:27017/")
db = client["project_db"]


# Collections
users_collection = db["users"]
content_collection = db["content"]
likes_collection = db["likes"]
comments_collection = db["comments"]
shares_collection = db["shares"]
notes_collection = db["notes"]
events_collection = db["events"]
conversations_collection = db["conversations"]


def init_indexes():
    users_collection.create_index("email", unique=True)
    users_collection.create_index("location")

    content_collection.create_index("tags")
    content_collection.create_index([("created_at", -1)])

    comments_collection.create_index("content_id")
    comments_collection.create_index("user_id")
    comments_collection.create_index([("created_at", -1)])

    shares_collection.create_index("content_id")
    shares_collection.create_index("from_user_id")
    shares_collection.create_index("to_user_id")

    notes_collection.create_index("user_id")
    notes_collection.create_index([("created_at", -1)])

    conversations_collection.create_index("user_id")
    conversations_collection.create_index([("created_at", -1)])

    print("✅ Mongo indexes initialized")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Users
def create_user(user_data):
    user_data["created_at"] = datetime.now(timezone.utc)

    if "location" not in user_data or not user_data["location"]:
        user_data["location"] = "Guadalajara"

    if "preferences" not in user_data or not isinstance(user_data["preferences"], list):
        user_data["preferences"] = []

    if "role" not in user_data:
        user_data["role"] = "user"

    if "password" in user_data:
        user_data["password"] = hash_password(user_data["password"])

    result = users_collection.insert_one(user_data)
    user_id = str(result.inserted_id)

    create_user_node(user_id, user_data["location"])

    return user_id


def get_user_by_email(email):
    return users_collection.find_one({"email": email})


def get_user_by_id(user_id):
    try:
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return None


def user_exists(email):
    return users_collection.find_one({"email": email}) is not None


def check_password(email, password):
    user = users_collection.find_one({"email": email})
    if not user:
        return None
    if user.get("password") == hash_password(password):
        return user
    return None


def update_user_field(user_id, field, value):
    try:
        obj_id = ObjectId(user_id)
    except:
        return False

    result = users_collection.update_one(
        {"_id": obj_id},
        {"$set": {field: value}}
    )

    if result.modified_count > 0 and field == "location":
        update_user_location(user_id, value)

    return result.modified_count > 0


def add_preference(user_id, preference):
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"preferences": preference}}
    )
    return result.modified_count > 0


def remove_preference(user_id, preference):
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"preferences": preference}}
    )
    return result.modified_count > 0


def is_admin(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return False
    return user.get("role") == "admin"


def get_all_users():
    users = list(users_collection.find().sort("created_at", 1))
    results = []

    for u in users:
        results.append({
            "user_id": str(u["_id"]),
            "email": u.get("email"),
            "first_name": u.get("first_name", ""),
            "last_name": u.get("last_name", ""),
            "location": u.get("location", ""),
            "role": u.get("role", "user"),
            "preferences": u.get("preferences", [])
        })

    return results


# Content
def create_content(content_data):
    content_data["created_at"] = datetime.now(timezone.utc)
    if "tags" not in content_data:
        content_data["tags"] = []
    result = content_collection.insert_one(content_data)
    return str(result.inserted_id)


def get_content_by_id(content_id):
    try:
        return content_collection.find_one({"_id": ObjectId(content_id)})
    except:
        return None


def content_exists(content_id):
    return get_content_by_id(content_id) is not None


def get_all_content():
    contents = list(content_collection.find().sort("created_at", -1))
    results = []

    for c in contents:
        results.append({
            "content_id": str(c["_id"]),
            "type": c.get("type", "text"),
            "title": c.get("title", ""),
            "body": c.get("body", ""),
            "tags": c.get("tags", []),
            "created_by": c.get("created_by", ""),
            "created_at": c.get("created_at").isoformat() if c.get("created_at") else ""
        })

    return results


# Likes
def like_content(user_id, content_id):
    existing = likes_collection.find_one({
        "user_id": user_id,
        "content_id": content_id
    })

    if existing:
        return None

    result = likes_collection.insert_one({
        "user_id": user_id,
        "content_id": content_id,
        "created_at": datetime.now(timezone.utc)
    })

    return str(result.inserted_id)


# Comments
def create_comment(user_id, content_id, text):
    comment = {
        "user_id": user_id,
        "content_id": content_id,
        "text": text,
        "created_at": datetime.now(timezone.utc)
    }
    result = comments_collection.insert_one(comment)
    return str(result.inserted_id)


def get_comments_by_content(content_id):
    comments = list(comments_collection.find({"content_id": content_id}))
    for c in comments:
        c["_id"] = str(c["_id"])
        if "created_at" in c:
            c["created_at"] = c["created_at"].isoformat()
    return comments


def get_comments_by_user(user_id):
    comments = list(comments_collection.find({"user_id": user_id}))
    for c in comments:
        c["_id"] = str(c["_id"])
        if "created_at" in c:
            c["created_at"] = c["created_at"].isoformat()
    return comments


# Shares
def share_content(from_user_id, to_user_id, content_id, platform="internal"):
    share = {
        "from_user_id": from_user_id,
        "to_user_id": to_user_id,
        "content_id": content_id,
        "platform": platform,
        "created_at": datetime.now(timezone.utc)
    }
    result = shares_collection.insert_one(share)
    return str(result.inserted_id)


# Notes
def create_note(user_id, text, title=""):
    note = {
        "user_id": user_id,
        "title": title,
        "text": text,
        "created_at": datetime.now(timezone.utc)
    }
    result = notes_collection.insert_one(note)
    return str(result.inserted_id)


def get_notes(user_id):
    notes = list(notes_collection.find({"user_id": user_id}).sort("created_at", -1))
    for n in notes:
        n["_id"] = str(n["_id"])
        n["created_at"] = n["created_at"].isoformat()
    return notes


def update_note(note_id, user_id, text):
    try:
        obj_id = ObjectId(note_id)
    except:
        return False
    result = notes_collection.update_one(
        {"_id": obj_id, "user_id": user_id},
        {"$set": {"text": text}}
    )
    return result.modified_count > 0


def delete_note(note_id, user_id):
    try:
        obj_id = ObjectId(note_id)
    except:
        return False
    result = notes_collection.delete_one({"_id": obj_id, "user_id": user_id})
    return result.deleted_count > 0


# Recommendations (content)
def recommend_content(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return []

    preferences = user.get("preferences", [])
    if isinstance(preferences, str):
        preferences = [preferences]
    preferences = [p.lower() for p in preferences if isinstance(p, str)]

    if not preferences:
        return []

    contents = list(content_collection.find())
    results = []

    for c in contents:
        tags = c.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        tags = [t.lower() for t in tags if isinstance(t, str)]

        match = any(tag in preferences for tag in tags)

        if match:
            results.append({
                "content_id": str(c["_id"]),
                "title": c.get("title"),
                "tags": tags
            })

    return results


# Metrics
def get_content_metrics():
    results = []
    contents = list(content_collection.find())

    for c in contents:
        cid = str(c["_id"])

        likes_count = likes_collection.count_documents({"content_id": cid})
        comments_count = comments_collection.count_documents({"content_id": cid})
        shares_count = shares_collection.count_documents({"content_id": cid})

        results.append({
            "content_id": cid,
            "title": c.get("title"),
            "likes": likes_count,
            "comments": comments_count,
            "shares": shares_count
        })

    return results


def get_trending_content(limit=10):
    contents = list(content_collection.find())
    results = []

    for c in contents:
        cid = str(c["_id"])
        likes = likes_collection.count_documents({"content_id": cid})
        comments = comments_collection.count_documents({"content_id": cid})
        shares = shares_collection.count_documents({"content_id": cid})

        score = likes + (comments * 2) + (shares * 3)

        results.append({
            "content_id": cid,
            "title": c.get("title"),
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


def get_system_stats():
    return {
        "total_users": users_collection.count_documents({}),
        "total_content": content_collection.count_documents({}),
        "total_likes": likes_collection.count_documents({}),
        "total_comments": comments_collection.count_documents({}),
        "total_shares": shares_collection.count_documents({}),
        "total_notes": notes_collection.count_documents({}),
        "total_events": events_collection.count_documents({}),
        "total_conversations": conversations_collection.count_documents({})
    }


# Events
def create_event(event_data):
    event_data["created_at"] = datetime.now(timezone.utc)
    result = events_collection.insert_one(event_data)
    event_id = str(result.inserted_id)
    create_event_node(event_id, event_data.get("title", ""))
    return event_id


def get_events_by_location(location):
    events = list(events_collection.find({"location": location}))
    results = []
    for e in events:
        results.append({
            "event_id": str(e["_id"]),
            "title": e.get("title"),
            "location": e.get("location"),
            "date": e.get("date"),
            "category": e.get("category")
        })
    return results


def get_event_by_id(event_id):
    try:
        e = events_collection.find_one({"_id": ObjectId(event_id)})
        if not e:
            return None
        return {
            "event_id": str(e["_id"]),
            "title": e.get("title"),
            "location": e.get("location"),
            "date": e.get("date"),
            "category": e.get("category")
        }
    except:
        return None


def get_all_events():
    events = list(events_collection.find().sort("created_at", -1))
    results = []

    for e in events:
        results.append({
            "event_id": str(e["_id"]),
            "title": e.get("title", ""),
            "location": e.get("location", ""),
            "date": e.get("date", ""),
            "category": e.get("category", "")
        })

    return results


# Conversations
def save_conversation(user_id, prompt, response):
    conv = {
        "user_id": user_id,
        "prompt": prompt,
        "response": response,
        "created_at": datetime.now(timezone.utc)
    }
    result = conversations_collection.insert_one(conv)
    return str(result.inserted_id)


def get_conversations(user_id):
    convs = list(conversations_collection.find({"user_id": user_id}).sort("created_at", -1))
    for c in convs:
        c["_id"] = str(c["_id"])
        c["created_at"] = c["created_at"].isoformat()
    return convs


# Reset
def reset_mongo():
    users_collection.delete_many({})
    content_collection.delete_many({})
    likes_collection.delete_many({})
    comments_collection.delete_many({})
    shares_collection.delete_many({})
    notes_collection.delete_many({})
    events_collection.delete_many({})
    conversations_collection.delete_many({})
