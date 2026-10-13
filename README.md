# ☁ Little Lounge - Watch Party

A small Flask + HTML/CSS/JavaScript watch-party demo. It is deliberately kept simple so it is easy to understand, run locally, and explain in a student project submission.

## Features

- Create a room or join with a five-character code; copy an invite link.
- Shared play, pause, seek, and video selection (host controls playback).
- Polling keeps participants updated and corrects playback drift when it exceeds 0.5 seconds.
- Movie discovery with search and category filters.
- Shared playlist, live chat, emoji reactions, group polls, and host transfer.
- Handles refresh/reconnection by fetching the latest room state again.
- Responsive layout, soft cream/pink/sage palette, and rounded cards.

## Run locally

Python 3.10+ recommended.

```bash
# 1. Open a terminal in this folder
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2. Install and start
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. Open a second browser/incognito window to test another participant. Create a room in one window, copy its code, and join it from the other.

## Important demo notes

- Rooms live in server memory. Restarting `app.py` clears all rooms; this is intentional for a small local project.
- This version uses short polling rather than a WebSocket service to keep the backend beginner-friendly. Room changes normally appear within about a second.
- Playback sync uses a server timestamp and clients correct drift greater than 0.5 seconds. Browser autoplay rules may require a user to click play once.
- The sample library uses public sample MP4 URLs. Availability depends on the network and browser. A custom link should point directly to a playable video file; ordinary YouTube watch-page URLs will not work in the HTML video element.
- This is a learning/demo app, not a production service: no database, login system, rate limiting, or private-room security. Anyone with a room code can join.

## Project structure

```text
watch_party/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## What I made creative

The app is called **Little Lounge**. I used a cozy “movie-night notebook” style: cream background, muted rose accents, sage green details, cute tiny emoji posters, and friendly copy. I kept the layout plain and the colors limited so it still feels like a small student-built project rather than a big commercial product.

## Quick test checklist

- [ ] Create a room and copy the invite.
- [ ] Join from a second browser window with a different nickname.
- [ ] Send chat messages and emoji reactions.
- [ ] Vote in a poll.
- [ ] Add a movie to the playlist.
- [ ] As host, play/pause/seek and switch the clip.
- [ ] Transfer host to the second participant and test playback controls.
- [ ] Refresh a participant tab and confirm it reconnects to the current room state.
