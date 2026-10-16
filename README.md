# Christian Content API — NoSQL Course Project

A Python/Falcon API and CLI exploring how document, wide-column, graph, and vector stores can support one Christian content application. Built for the Non-Relational Databases course.

## Provenance and my contribution

The project started from an existing application supplied by the course professor. I made the subsequent modifications for this submission. The public history begins with a complete delivery commit, so it does not isolate those modifications from the supplied baseline. The database architecture and original application should not be attributed entirely to me. The professor and course retain credit for the starting project.

[Source and submission history](https://github.com/mr-Mariano/christian-content-api/commits/main/)

## Architecture

```text
Python CLI -> Falcon API -> MongoDB / Cassandra / Dgraph
                        -> embedded ChromaDB (./chroma_data)
```

| Store | Role in the source |
| --- | --- |
| MongoDB | Users, content, comments, notes, shares, events, conversations |
| Cassandra | Activity history, daily activity, content engagement |
| Dgraph | Follow relationships, event attendance, graph recommendations |
| ChromaDB | Content vectors and similarity retrieval |

The API includes registration/login, content browsing, likes/comments/shares, personal notes, preferences, social and event recommendations, analytics, search, and stored chatbot conversations. There is no separate web frontend.

### Search and chatbot behavior

`db/chroma.py` builds normalized 128-dimensional hashed token-count vectors locally. This is a lightweight similarity demonstration, not a pretrained semantic embedding model. `routes/chatbot.py` retrieves up to three items and assembles excerpts using a fixed response template. It does not call an external LLM.

The split between stores demonstrates different access patterns, while adding service startup requirements and cross-store consistency work. There is no distributed transaction covering all four stores.

## Local setup

Prerequisites: Python 3 with virtual environment support, Docker with Docker Compose, and `make`. Gunicorn is intended for a Unix-like environment; Windows users can use WSL.

```bash
git clone https://github.com/mr-Mariano/christian-content-api.git
cd christian-content-api
make install
make up
make run-api
```

The API binds to `http://localhost:8000`. Compose exposes MongoDB on 27017, Cassandra on 9042, and Dgraph on 8080/9080. ChromaDB runs inside Python and persists under `chroma_data/`; it is not a fourth container. Wait for the database services to finish initializing, especially Cassandra, before starting the API.

In another terminal, from the repository root:

```bash
make seed
.venv/bin/python cli.py login --email admin@mail.com --password 123456
.venv/bin/python cli.py list-content
.venv/bin/python cli.py list-events
.venv/bin/python cli.py search-content --query "short prayer for anxiety"
.venv/bin/python cli.py chatbot --prompt "Suggest something to read before sleeping"
.venv/bin/python cli.py --help
```

**`make seed` resets existing application data before inserting demo records.** Use disposable local databases. It creates an admin and four users, interactions, events, and sample conversations, and writes IDs to `seed_results.json`. Demo passwords are `123456` and are for local demonstration only.

The CLI and seed script accept `API_URL`, defaulting to `http://localhost:8000`. Use the virtual environment's Python as shown; `make install` does not activate it in your shell.

```bash
make logs
make down
```

`make down` stops the containers. Treat the Compose database storage as disposable: no named persistence volumes are declared.

## Code map and API

- `app.py`: resource registration and startup initialization.
- `routes/`: authentication, content, interactions, recommendations, search, chatbot, and statistics.
- `db/`: database clients, schemas, queries, and vector construction.
- `cli.py`: demonstration client; `seed_data.py`: reproducible sample scenario.

Representative routes: `POST /register`, `POST /login`, `GET /content`, `GET /recommend/content/{user_id}`, `GET /search-content`, `POST /chatbot`, and `GET /system-stats`. Consult `app.py` and `cli.py --help` for the complete interface.

## Limitations and validation

This is an academic prototype. Passwords use SHA-256 in the current source, and identity/authorization handling needs hardening before deployment. The reset endpoint and demo credentials belong in an isolated local environment. Dependencies are unpinned and the Dgraph image uses `latest`, which can affect reproducibility.

The seed and CLI provide a manual demonstration path; they do not establish automated coverage or production readiness. No hosted demo is documented here.
