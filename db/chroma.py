import hashlib
import math
import re

import chromadb

client = chromadb.PersistentClient(path="./chroma_data")

collection = client.get_or_create_collection(
    name="content_embeddings"
)

EMBEDDING_SIZE = 128


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def build_embedding(text):
    tokens = tokenize(text)
    vector = [0.0] * EMBEDDING_SIZE

    if not tokens:
        return vector

    for token in tokens:
        digest = hashlib.md5(token.encode()).hexdigest()
        idx = int(digest, 16) % EMBEDDING_SIZE
        vector[idx] += 1.0

    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector

    return [v / norm for v in vector]


def add_content_embedding(content_id, title, body, tags):
    if not isinstance(tags, list):
        tags = []

    text = f"""
    Title: {title}
    Body: {body}
    Tags: {' '.join(tags)}
    """

    embedding = build_embedding(text)

    collection.upsert(
        ids=[content_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{
            "content_id": content_id,
            "title": title
        }]
    )


def semantic_search(query, limit=5):

    embedding = build_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=limit
    )

    matches = []

    if not results["ids"] or not results["ids"][0]:
        return matches

    ids = results["ids"][0]
    metas = results["metadatas"][0]

    for i in range(len(ids)):
        matches.append({
            "content_id": metas[i]["content_id"],
            "title": metas[i]["title"]
        })

    return matches


def retrieve_for_rag(query, limit=3):
    """same as semantic_search but returns the document text too, for the chatbot"""
    embedding = build_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=limit
    )

    docs = []

    if not results["ids"] or not results["ids"][0]:
        return docs

    ids = results["ids"][0]
    documents = results["documents"][0]
    metas = results["metadatas"][0]

    for i in range(len(ids)):
        docs.append({
            "content_id": metas[i]["content_id"],
            "title": metas[i]["title"],
            "text": documents[i]
        })

    return docs


def reset_chroma():
    global collection
    try:
        client.delete_collection("content_embeddings")
    except:
        pass
    collection = client.get_or_create_collection(name="content_embeddings")
