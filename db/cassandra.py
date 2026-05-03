from cassandra.cluster import Cluster
from datetime import datetime
import time


cluster = Cluster(
    ["localhost"],
    port=9042,
    connect_timeout=10
)

session = None

for i in range(25):
    try:
        session = cluster.connect()

        session.execute("SELECT now() FROM system.local")

        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS project
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
        """)

        session.set_keyspace("project")
        break

    except Exception as e:
        print(f"⏳ Waiting for Cassandra... ({i+1}/25)")
        time.sleep(3)


if session is None:
    raise Exception("❌ Could not connect to Cassandra")


# activity_by_user — query by user_id, ordered by time
session.execute("""
CREATE TABLE IF NOT EXISTS activity_by_user (
    user_id text,
    timestamp timestamp,
    action text,
    content_id text,
    PRIMARY KEY (user_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
""")


# activity_by_day — daily active users, daily analytics
session.execute("""
CREATE TABLE IF NOT EXISTS activity_by_day (
    date text,
    timestamp timestamp,
    user_id text,
    action text,
    content_id text,
    PRIMARY KEY (date, timestamp, user_id)
) WITH CLUSTERING ORDER BY (timestamp DESC, user_id ASC)
""")


# activity_by_content — engagement per content, trending
session.execute("""
CREATE TABLE IF NOT EXISTS activity_by_content (
    content_id text,
    timestamp timestamp,
    user_id text,
    action text,
    PRIMARY KEY (content_id, timestamp, user_id)
) WITH CLUSTERING ORDER BY (timestamp DESC, user_id ASC)
""")


session.execute("""
CREATE TABLE IF NOT EXISTS daily_active_users (
    date text PRIMARY KEY,
    users set<text>
)
""")


def log_activity(user_id, action, content_id=""):
    now = datetime.utcnow()
    day = now.date().isoformat()

    session.execute(
        """
        INSERT INTO activity_by_user (user_id, timestamp, action, content_id)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, now, action, content_id)
    )

    session.execute(
        """
        INSERT INTO activity_by_day (date, timestamp, user_id, action, content_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (day, now, user_id, action, content_id)
    )

    if content_id:
        session.execute(
            """
            INSERT INTO activity_by_content (content_id, timestamp, user_id, action)
            VALUES (%s, %s, %s, %s)
            """,
            (content_id, now, user_id, action)
        )

    session.execute(
        """
        UPDATE daily_active_users
        SET users = users + %s
        WHERE date = %s
        """,
        ({user_id}, day)
    )

    print(f"📊 Logged in Cassandra: {action}")


def get_activity_by_user(user_id):
    rows = session.execute(
        "SELECT * FROM activity_by_user WHERE user_id = %s",
        (user_id,)
    )

    results = []

    for r in rows:
        results.append({
            "user_id": r.user_id,
            "action": r.action,
            "content_id": r.content_id,
            "timestamp": str(r.timestamp)
        })

    return results


def get_activity_by_user_filtered(user_id, action_type=None):
    rows = session.execute(
        "SELECT * FROM activity_by_user WHERE user_id = %s",
        (user_id,)
    )

    results = []

    for r in rows:
        if action_type and r.action != action_type:
            continue

        results.append({
            "action": r.action,
            "content_id": r.content_id,
            "timestamp": str(r.timestamp)
        })

    return results


def get_activity_by_day(date):
    rows = session.execute(
        "SELECT * FROM activity_by_day WHERE date = %s",
        (date,)
    )

    results = []
    for r in rows:
        results.append({
            "user_id": r.user_id,
            "action": r.action,
            "content_id": r.content_id,
            "timestamp": str(r.timestamp)
        })
    return results


def get_activity_by_content(content_id):
    rows = session.execute(
        "SELECT * FROM activity_by_content WHERE content_id = %s",
        (content_id,)
    )

    results = []
    for r in rows:
        results.append({
            "user_id": r.user_id,
            "action": r.action,
            "timestamp": str(r.timestamp)
        })
    return results


def get_content_stats(content_id):
    rows = session.execute(
        "SELECT action FROM activity_by_content WHERE content_id = %s",
        (content_id,)
    )

    counts = {}
    for r in rows:
        counts[r.action] = counts.get(r.action, 0) + 1
    return counts


def get_daily_active_users(date=None):
    if date:
        row = session.execute(
            "SELECT users FROM daily_active_users WHERE date = %s",
            (date,)
        ).one()
        users = row.users if row and row.users else set()
        return [{"date": date, "active_users": len(users)}]

    rows = session.execute("SELECT date, users FROM daily_active_users")
    result = []
    for r in rows:
        result.append({
            "date": r.date,
            "active_users": len(r.users or set())
        })

    result.sort(key=lambda x: x["date"])
    return result


def reset_cassandra():
    session.execute("TRUNCATE activity_by_user")
    session.execute("TRUNCATE activity_by_day")
    session.execute("TRUNCATE activity_by_content")
    session.execute("TRUNCATE daily_active_users")
