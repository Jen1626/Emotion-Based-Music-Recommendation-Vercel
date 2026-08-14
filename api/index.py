import base64
import os
import time
from pathlib import Path

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

TOKEN = {"value": None, "expires": 0}

MOODS = {
    "happy": "happy upbeat pop",
    "sad": "sad acoustic",
    "angry": "rock energetic",
    "surprised": "party pop edm",
    "neutral": "lofi chill",
    "fearful": "calm ambient",
    "disgusted": "uplifting alternative",
}

FALLBACKS = {
    "happy": {
        "name": "Happy",
        "artist": "Pharrell Williams",
        "album": "G I R L",
        "spotify_url": "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH",
    },
    "sad": {
        "name": "Someone Like You",
        "artist": "Adele",
        "album": "21",
        "spotify_url": "https://open.spotify.com/track/1zwMYTA5nlNjZb4q8VfH4D",
    },
    "angry": {
        "name": "Believer",
        "artist": "Imagine Dragons",
        "album": "Evolve",
        "spotify_url": "https://open.spotify.com/track/0pqnGHJpmpxLKifKRmU6WP",
    },
    "surprised": {
        "name": "Don't Start Now",
        "artist": "Dua Lipa",
        "album": "Future Nostalgia",
        "spotify_url": "https://open.spotify.com/track/3PfIrDoz19wz7qK7tYeu62",
    },
    "neutral": {
        "name": "Sunset Lover",
        "artist": "Petit Biscuit",
        "album": "Presence",
        "spotify_url": "https://open.spotify.com/track/0dGk1v4uJQqk6t4a8q8J5Q",
    },
    "fearful": {
        "name": "Weightless",
        "artist": "Marconi Union",
        "album": "Weightless",
        "spotify_url": "https://open.spotify.com/track/6Qn5zhYkTa37e91HC1D7lb",
    },
    "disgusted": {
        "name": "Good as Hell",
        "artist": "Lizzo",
        "album": "Cuz I Love You",
        "spotify_url": "https://open.spotify.com/track/3Yh9lZcWyKrK9GjbHw1mG6",
    },
}


def fallback_song(emotion):
    song = dict(FALLBACKS.get(emotion, FALLBACKS["neutral"]))
    song.update({"emotion": emotion, "source": "fallback"})
    return song


def spotify_token():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    now = time.time()

    if TOKEN["value"] and now < TOKEN["expires"] - 30:
        return TOKEN["value"]

    encoded = base64.b64encode(
        f"{client_id}:{client_secret}".encode()
    ).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    TOKEN["value"] = data["access_token"]
    TOKEN["expires"] = now + int(data.get("expires_in", 3600))

    return TOKEN["value"]


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "Moodrix"})


@app.get("/api/get_song")
def get_song():
    emotion = request.args.get("emotion", "neutral").lower().strip()

    if emotion not in MOODS:
        emotion = "neutral"

    try:
        token = spotify_token()

        if not token:
            return jsonify(fallback_song(emotion))

        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "q": MOODS[emotion],
                "type": "track",
                "limit": 10,
            },
            timeout=10,
        )

        response.raise_for_status()

        tracks = response.json().get("tracks", {}).get("items", [])

        if not tracks:
            return jsonify(fallback_song(emotion))

        track = tracks[0]
        images = track.get("album", {}).get("images", [])

        return jsonify(
            {
                "emotion": emotion,
                "name": track.get("name", "Unknown song"),
                "artist": ", ".join(
                    a.get("name", "") for a in track.get("artists", [])
                ),
                "album": track.get("album", {}).get("name", ""),
                "image": images[0]["url"] if images else "",
                "spotify_url": track.get("external_urls", {}).get("spotify", ""),
                "preview_url": track.get("preview_url") or "",
                "source": "spotify",
            }
        )

    except Exception as error:
        print("Spotify error:", error)
        return jsonify(fallback_song(emotion))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000"))
    )
