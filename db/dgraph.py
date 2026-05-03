import pydgraph
import json


client_stub = pydgraph.DgraphClientStub('localhost:9080')
client = pydgraph.DgraphClient(client_stub)


def init_schema():
    schema = """
    user_id: string @index(exact) .
    follows: [uid] @reverse .
    location: string @index(term, exact) .

    event_id: string @index(exact) .
    title: string .

    attends: [uid] @reverse .
    """

    op = pydgraph.Operation(schema=schema)
    client.alter(op)

    print("✅ Dgraph schema initialized")


def create_user_node(user_id, location="unknown"):
    txn = client.txn()
    try:
        # avoid duplicates
        q = f'{{ u(func: eq(user_id, "{user_id}")) {{ uid }} }}'
        res = txn.query(q)
        data = json.loads(res.json)
        if data.get("u"):
            return

        user = {
            "uid": "_:user",
            "user_id": user_id,
            "location": location
        }

        txn.mutate(set_obj=user)
        txn.commit()

    finally:
        txn.discard()


def update_user_location(user_id, location):
    txn = client.txn()
    try:
        q = f'{{ u(func: eq(user_id, "{user_id}")) {{ uid }} }}'
        res = txn.query(q)
        data = json.loads(res.json)

        if not data.get("u"):
            create_user_node(user_id, location)
            return True

        txn.mutate(set_obj={
            "uid": data["u"][0]["uid"],
            "location": location
        })
        txn.commit()
        return True
    except Exception:
        return False
    finally:
        txn.discard()


def follow_user(follower_id, followee_id):
    if follower_id == followee_id:
        return False, "cannot follow yourself"

    txn = client.txn()
    try:
        q_uids = f"""
        {{
          follower(func: eq(user_id, "{follower_id}")) {{ uid }}
          followee(func: eq(user_id, "{followee_id}")) {{ uid }}
        }}
        """
        res = txn.query(q_uids)
        data = json.loads(res.json)

        if not data.get("follower") or not data.get("followee"):
            return False, "user not found"

        follower_uid = data["follower"][0]["uid"]
        followee_uid = data["followee"][0]["uid"]


        q_exists = f"""
        {{
          rel(func: uid({follower_uid})) @cascade {{
            uid
            follows @filter(uid({followee_uid})) {{ uid }}
          }}
        }}
        """
        res2 = txn.query(q_exists)
        data2 = json.loads(res2.json)


        if data2.get("rel"):
            return False, "already following"


        mutation = {
            "uid": follower_uid,
            "follows": [{"uid": followee_uid}]
        }

        txn.mutate(set_obj=mutation)
        txn.commit()

        return True, "followed"

    except Exception as e:
        return False, "internal error"
    finally:
        txn.discard()


def recommend_users(user_id):
    """friend-of-friend: users followed by people I follow, that I don't follow yet"""
    txn = client.txn()

    try:
        query = f"""
        {{
          me(func: eq(user_id, "{user_id}")) {{
            uid
            following: follows {{
              user_id
              fof: follows {{
                user_id
              }}
            }}
          }}
        }}
        """

        res = txn.query(query)
        data = json.loads(res.json)

        if not data.get("me"):
            return []

        me = data["me"][0]

        already = set([user_id])
        for f in me.get("following", []):
            if f.get("user_id"):
                already.add(f["user_id"])

        recommendations = set()
        for f in me.get("following", []):
            for fof in f.get("fof", []):
                uid = fof.get("user_id")
                if uid and uid not in already:
                    recommendations.add(uid)

        return list(recommendations)

    finally:
        txn.discard()


def recommend_users_by_location(user_id):
    txn = client.txn()

    try:
        query = f"""
        {{
          me(func: eq(user_id, "{user_id}")) {{
            uid
            location
            follows {{
              user_id
            }}
          }}
        }}
        """

        res = txn.query(query)
        data = json.loads(res.json)

        if not data.get("me"):
            return []

        me = data["me"][0]
        location = me.get("location")

        if not location:
            return []

        already = set([user_id])
        for f in me.get("follows", []):
            if f.get("user_id"):
                already.add(f["user_id"])


        query2 = f"""
        {{
          users(func: eq(location, "{location}")) {{
            user_id
          }}
        }}
        """

        res2 = txn.query(query2)
        data2 = json.loads(res2.json)

        recommendations = []

        for u in data2.get("users", []):
            uid = u.get("user_id")

            if not uid:
                continue
            if uid in already:
                continue

            recommendations.append(uid)

        return recommendations

    finally:
        txn.discard()


def create_event_node(event_id, title):
    txn = client.txn()

    try:
        # avoid duplicates
        q = f'{{ e(func: eq(event_id, "{event_id}")) {{ uid }} }}'
        res = txn.query(q)
        data = json.loads(res.json)
        if data.get("e"):
            return

        event = {
            "uid": "_:event",
            "event_id": event_id,
            "title": title
        }

        txn.mutate(set_obj=event)
        txn.commit()

    finally:
        txn.discard()


def attend_event(user_id, event_id):
    txn = client.txn()
    try:
        query = f"""
        {{
          user(func: eq(user_id, "{user_id}")) {{
            uid
            attends @filter(eq(event_id, "{event_id}")) {{ uid }}
          }}
          event(func: eq(event_id, "{event_id}")) {{
            uid
          }}
        }}
        """

        res = txn.query(query)
        data = json.loads(res.json)

        if not data.get("user") or not data.get("event"):
            return False

        # already attending
        if data["user"][0].get("attends"):
            return False

        user_uid = data["user"][0]["uid"]
        event_uid = data["event"][0]["uid"]

        mutation = {
            "uid": user_uid,
            "attends": [{"uid": event_uid}]
        }

        txn.mutate(set_obj=mutation)
        txn.commit()

        return True
    finally:
        txn.discard()


def get_user_events(user_id):
    txn = client.txn()

    try:
        query = f"""
        {{
          user(func: eq(user_id, "{user_id}")) {{
            attends {{
              event_id
              title
            }}
          }}
        }}
        """

        res = txn.query(query)
        data = json.loads(res.json)

        if not data.get("user"):
            return []

        events = data["user"][0].get("attends", [])

        if isinstance(events, dict):
            events = [events]

        return events
    finally:
        txn.discard()


def recommend_events_by_connections(user_id):
    """events that people I follow are attending, excluding events I'm already in"""
    txn = client.txn()

    try:
        query = f"""
        {{
          me(func: eq(user_id, "{user_id}")) {{
            already: attends {{
              event_id
            }}
            follows {{
              attends {{
                event_id
                title
              }}
            }}
          }}
        }}
        """

        res = txn.query(query)
        data = json.loads(res.json)

        if not data.get("me"):
            return []

        me = data["me"][0]

        already = set()
        for e in me.get("already", []):
            if e.get("event_id"):
                already.add(e["event_id"])

        seen = set()
        results = []

        for f in me.get("follows", []):
            for e in f.get("attends", []):
                eid = e.get("event_id")
                if not eid or eid in already or eid in seen:
                    continue
                seen.add(eid)
                results.append({
                    "event_id": eid,
                    "title": e.get("title")
                })

        return results
    finally:
        txn.discard()


def reset_dgraph():
    op = pydgraph.Operation(drop_all=True)
    client.alter(op)
    init_schema()
