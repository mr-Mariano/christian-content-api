# Christian Content App - Final Project

This repository contains our final project for the Non-Relational Databases course.

The idea of the app is inspired by platforms like Hallow: a space where users can find Christian content such as guided prayers, Bible reflections, short meditations, gratitude content, and community events. We wanted the project to feel modern, but still simple enough to build as a semester project.

The main goal was not to make a huge production system, but to show how different non-relational databases can solve different parts of the same application.

## What is in this project

The project includes:

- a Falcon backend API
- a Python CLI that works as our client for testing the app
- MongoDB, Cassandra, Dgraph and ChromaDB
- Docker Compose to run the databases

Important:

- In this repo we do not have a separate web frontend.
- For the final delivery, the CLI is the client we use to interact with the backend and demonstrate the requirements.

## General idea of the app

Users can:

- register and log in
- update profile data and spiritual preferences
- browse and receive recommended Christian content
- like, comment and share content
- create personal notes
- follow other users
- attend events
- search content semantically
- interact with a simple chatbot that uses stored content as context

## Why we used each database

We tried to use each database for the type of problem where it made sense:

- MongoDB:
  users, content, comments, notes, shares, events and conversations
- Cassandra:
  activity history, daily active users and content analytics
- Dgraph:
  follow relationships, user recommendations and event attendance relationships
- ChromaDB:
  semantic search and retrieval for the chatbot

## Project structure

```text
app.py
cli.py
seed_data.py
db/
routes/
docker-compose.yml
requirements.txt
Makefile
README.md
```

## Prerequisites

Before running the project, make sure you have:

- Python 3 installed
- Docker Desktop installed and running
- `make` available in your terminal

## Installation

From the project folder:

```bash
make install
```

This creates the virtual environment and installs the Python dependencies.

## Running the databases

To start MongoDB, Cassandra and Dgraph:

```bash
make up
```

To stop them:

```bash
make down
```

To see container logs:

```bash
make logs
```

Note:

- Cassandra usually takes the longest to start.
- If the API fails on the first try, wait a little and run it again.

## Running the backend

Once the containers are up, start the backend in a different terminal:

```bash
make run-api
```

The API runs on:

```text
http://localhost:8000
```

## Running the frontend

For this delivery, there is no separate frontend app in the repository.

Instead, we use:

- `cli.py` as the client
- JSON API responses to validate each requirement

So in practical terms:

- backend = Falcon API
- frontend/client for demo = Python CLI

## Environment variables

This project does not depend on a large `.env` setup.

The only optional variable we added is:

- `API_URL`

By default, the CLI and the seed use:

```text
http://localhost:8000
```

If needed, you can run commands like this:

```bash
API_URL=http://localhost:8000 python cli.py list-users
```

## Resetting the data

With the API already running:

```bash
make reset-db
```

This clears the application data from the databases used by the project.

## Seed data

We added a seed script to make the demo easier and reproducible.

Run:

```bash
make seed
```

What the seed does:

- resets current data
- creates an admin user and four normal users
- creates Christian/spiritual content
- creates community events
- creates likes, comments and shares
- creates notes
- creates follow relationships
- creates event attendance
- creates one chatbot conversation
- runs some recommendation and search queries
- saves generated IDs in `seed_results.json`

## Seeded accounts

All seeded users use the same password:

```text
123456
```

Users:

- `admin@mail.com` - admin
- `alice@mail.com`
- `bob@mail.com`
- `carla@mail.com`
- `diego@mail.com`

## Quick start

If you want the shortest version:

Terminal 1:

```bash
cd "/Users/mrmariano/Documents/LEARNING/ITESO/Semestre 4/Bases de Datos No Relacionales/Project/FinalDelivery"
make install
make up
make run-api
```

Terminal 2:

```bash
cd "/Users/mrmariano/Documents/LEARNING/ITESO/Semestre 4/Bases de Datos No Relacionales/Project/FinalDelivery"
make seed
python cli.py list-users
python cli.py list-content
python cli.py list-events
```

## Basic CLI commands

Login:

```bash
python cli.py login --email admin@mail.com --password 123456
```

Check current session:

```bash
python cli.py whoami
```

Logout:

```bash
python cli.py logout
```

Useful listing commands:

```bash
python cli.py list-users
python cli.py list-content
python cli.py list-events
python cli.py get-system-stats
```

## How we tested the main requirements

After running `make seed`, the easiest way is to use the IDs from:

- `seed_results.json`
- `python cli.py list-users`
- `python cli.py list-content`
- `python cli.py list-events`

### 1. Register, login and logout

```bash
python cli.py register --email test@mail.com --password 123456 --preferences prayer bible --first-name Test --last-name User --location Guadalajara
python cli.py login --email test@mail.com --password 123456
python cli.py whoami
python cli.py logout
```

### 2. Update profile and preferences

```bash
python cli.py login --email alice@mail.com --password 123456
python cli.py update-user --field location --value Zapopan
python cli.py add-preference --preference gratitude
python cli.py remove-preference --preference gratitude
```

### 3. Create content and get content recommendations

Only the admin can create content:

```bash
python cli.py login --email admin@mail.com --password 123456
python cli.py create-content --type prayer --title "Morning Prayer Before Class" --body "A short prayer to begin the day with focus and peace." --tags prayer morning focus
python cli.py list-content
python cli.py logout
python cli.py login --email alice@mail.com --password 123456
python cli.py recommend-content
```

### 4. Like content

```bash
python cli.py like-content --id CONTENT_ID
```

### 5. Comment on content

```bash
python cli.py comment --content-id CONTENT_ID --text "This one felt simple and helpful."
python cli.py comments-by-content --content-id CONTENT_ID
python cli.py comments-by-user
```

### 6. Follow users and get recommendations

```bash
python cli.py follow-user --user-id USER_ID
python cli.py recommend-users
python cli.py recommend-users-by-location
```

### 7. Share content

Internal share:

```bash
python cli.py share-content --content-id CONTENT_ID --user-id USER_ID
```

External share:

```bash
python cli.py share-external --content-id CONTENT_ID --platform whatsapp
```

### 8. Notes

```bash
python cli.py create-note --title "Prayer note" --text "Come back to the night prayer this week."
python cli.py get-notes
python cli.py update-note --id NOTE_ID --text "Come back to the night prayer and Psalm 23 this week."
python cli.py delete-note --id NOTE_ID
```

### 9. Events

Create event as admin:

```bash
python cli.py login --email admin@mail.com --password 123456
python cli.py create-event --title "Evening Worship Gathering" --location Guadalajara --date 2026-05-30 --category worship
python cli.py list-events
```

Get events by location:

```bash
python cli.py get-local-events --location Guadalajara
```

Attend event and get recommendations:

```bash
python cli.py logout
python cli.py login --email alice@mail.com --password 123456
python cli.py attend-event --event-id EVENT_ID
python cli.py my-events
python cli.py recommend-events-by-connections
```

### 10. Activity and analytics

```bash
python cli.py get-activity-history
python cli.py get-activity-history --type like
python cli.py get-daily-active-users
python cli.py stats-by-content --content-id CONTENT_ID
python cli.py metrics-content
python cli.py trending-content
python cli.py get-system-stats
```

### 11. Semantic search

```bash
python cli.py search-content --query "short prayer for anxiety"
python cli.py search-content --query "gospel reflection for a busy day"
```

### 12. Chatbot

```bash
python cli.py chatbot --prompt "Can you suggest something short to pray before sleeping?"
python cli.py conversations
```

## Main routes

Auth:

- `POST /register`
- `POST /login`
- `POST /logout`

Users:

- `GET /users`
- `POST /user/update`
- `POST /user/add-preference`
- `POST /user/remove-preference`

Content:

- `GET /content`
- `POST /content`
- `GET /recommend/content/{user_id}`
- `GET /metrics/content`
- `GET /metrics/content/{content_id}`
- `GET /trending`

Interactions:

- `POST /like`
- `POST /comment`
- `GET /comments/{content_id}`
- `GET /comments/user/{user_id}`
- `POST /share`
- `POST /share-external`

Notes:

- `POST /notes`
- `GET /notes/{user_id}`
- `POST /notes/update`
- `POST /notes/delete/{note_id}`

Social graph and events:

- `POST /follow`
- `GET /recommend/users/{user_id}`
- `GET /recommend/location/{user_id}`
- `GET /event`
- `POST /event`
- `GET /events`
- `POST /attend-event`
- `GET /my-events/{user_id}`
- `GET /recommend/events/{user_id}`

Search, chatbot and stats:

- `GET /search-content`
- `POST /chatbot`
- `GET /conversations/{user_id}`
- `GET /activity/{user_id}`
- `GET /activity-filter/{user_id}`
- `GET /dau`
- `GET /system-stats`
- `POST /reset`

