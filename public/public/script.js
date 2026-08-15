let stream = null;
let running = false;
let lastEmotion = "";
let lastRecommendation = 0;

const MODEL_URL = "https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model";

const pretty = {
  happy: "Happy",
  sad: "Sad",
  angry: "Angry",
  surprised: "Surprised",
  neutral: "Neutral",
  fearful: "Fearful",
  disgusted: "Disgusted"
};

const $ = (id) => document.getElementById(id);

async function startApp() {
  const button = $("startBtn");
  button.disabled = true;
  $("startStatus").textContent = "Loading facial-expression model...";

  try {
    if (!window.faceapi) {
      throw new Error("Face detection library did not load.");
    }

    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
      faceapi.nets.faceExpressionNet.loadFromUri(MODEL_URL)
    ]);

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error("Camera access is not available. Use the HTTPS Vercel URL.");
    }

    $("startStatus").textContent = "Requesting camera access...";

    stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user",
        width: { ideal: 720 },
        height: { ideal: 540 }
      },
      audio: false
    });

    $("video").srcObject = stream;
    await $("video").play();

    $("landing").classList.add("hidden");
    $("dashboard").classList.remove("hidden");
    $("cameraState").textContent = "● LIVE";
    running = true;

    detectLoop();
  } catch (error) {
    console.error(error);
    button.disabled = false;
    $("startStatus").textContent =
      "Could not start. Allow camera access, reload the page, and use the HTTPS Vercel URL.";
  }
}

function dominant(expressions) {
  return Object.entries(expressions).sort((a, b) => b[1] - a[1])[0];
}

async function detectLoop() {
  if (!running) return;

  try {
    const result = await faceapi
      .detectSingleFace(
        $("video"),
        new faceapi.TinyFaceDetectorOptions({
          inputSize: 320,
          scoreThreshold: 0.5
        })
      )
      .withFaceExpressions();

    if (!result) {
      $("emotion").textContent = "No face";
      $("confidence").textContent = "Move into the camera frame.";
    } else {
      const [emotion, confidence] = dominant(result.expressions);

      $("emotion").textContent = pretty[emotion] || emotion;
      $("confidence").textContent =
        Math.round(confidence * 100) + "% confidence";

      const now = Date.now();

      if (emotion !== lastEmotion || now - lastRecommendation > 30000) {
        lastEmotion = emotion;
        lastRecommendation = now;
        recommend(emotion);
      }
    }
  } catch (error) {
    console.error(error);
    $("apiStatus").textContent =
      "Emotion detection is temporarily unavailable.";
  }

  setTimeout(detectLoop, 1200);
}

async function recommend(emotion) {
  $("apiStatus").textContent = "Finding a recommendation...";

  try {
    const response = await fetch(
      "/api/get_song?emotion=" + encodeURIComponent(emotion),
      { headers: { "Accept": "application/json" } }
    );

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || "Recommendation failed");
    }

    $("songName").textContent = data.name || "Unknown song";
    $("artist").textContent = data.artist || "Unknown artist";
    $("album").textContent = data.album || "";

    if (data.image) {
      $("albumArt").src = data.image;
      $("albumArt").classList.add("show");
      $("albumPlaceholder").classList.add("hidden");
    } else {
      $("albumArt").removeAttribute("src");
      $("albumArt").classList.remove("show");
      $("albumPlaceholder").classList.remove("hidden");
    }

    if (data.spotify_url) {
      $("spotify").href = data.spotify_url;
      $("spotify").classList.add("show");
    } else {
      $("spotify").removeAttribute("href");
      $("spotify").classList.remove("show");
    }

    $("apiStatus").textContent =
      data.source === "spotify"
        ? "Recommendation from Spotify."
        : "Demo recommendation ready. Add Spotify credentials in Vercel for live Spotify search.";
  } catch (error) {
    console.error(error);
    $("apiStatus").textContent =
      "Could not load a recommendation. The demo fallback may be unavailable.";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  $("startBtn").addEventListener("click", startApp);
});

window.addEventListener("beforeunload", () => {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
  }
});
