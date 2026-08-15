# Moodrix — Emotion-Based Music Recommendation

**Live Demo:** https://emotion-based-music-recommendation-fawn.vercel.app/

Moodrix is an AI-powered music recommendation web application that uses facial-expression recognition in the browser to detect a user's current emotion and recommend music that matches the detected mood.

## Features

- Browser-based facial emotion detection
- Live camera preview
- Happy, sad, angry, surprised, neutral, fearful and disgusted emotion classes
- Mood-based music recommendations
- Spotify integration through a Vercel Python API
- Fallback recommendations when Spotify credentials are not configured
- Responsive web interface
- Camera frames are processed in the browser and are not uploaded to the backend

## Vercel deployment

Upload the contents of this folder to the root of your GitHub repository and import that repository into Vercel.

Required root files:

- `index.html`
- `style.css`
- `script.js`
- `vercel.json`
- `requirements.txt`
- `api/index.py`

The project does not require Node.js or a package.json file.

### Optional Spotify credentials

For live Spotify search, add these Vercel Environment Variables:

`SPOTIFY_CLIENT_ID`

`SPOTIFY_CLIENT_SECRET`

The application still works with demo fallback recommendations without these variables.

## Camera permission

Use the HTTPS Vercel deployment URL and click **Start Mood Detection**. Allow camera access when the browser asks.


