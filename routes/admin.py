import json
from db.mongo import reset_mongo
from db.cassandra import reset_cassandra
from db.chroma import reset_chroma
from db.dgraph import reset_dgraph


class ResetResource:
    def on_post(self, req, resp):
        reset_mongo()
        reset_cassandra()

        try:
            reset_chroma()
        except Exception as e:
            print(f"⚠️  Could not reset chroma: {e}")

        try:
            reset_dgraph()
        except Exception as e:
            print(f"⚠️  Could not reset dgraph: {e}")

        resp.text = json.dumps({"message": "data reset"})
