# 🎙 VoiceForge — AI Text-to-Speech & Speech-to-Text Platform

A full-stack voice platform built with FastAPI, MongoDB, Edge TTS, Whisper, and a dark-mode web frontend.

- **Text to Speech:** turn any text into natural speech with 20 neural voices in 6 languages.
- **Speech to Text:** record your voice or upload an audio file and get the transcript back.

---

## ✨ What's New

### Landing page
- The headline types out rotating words ("Give your stories / podcasts / lessons a voice").
- Animated sound rings behind the hero, a scroll progress bar, and a navigation bar that darkens as you scroll.
- The live demo has example scripts (Welcome, Story, Ad, News), a character counter and an equalizer that moves while audio plays.
- Visitors who aren't signed in hear a preview in the browser's built-in voice, with a link to sign up for the neural voices. Signed-in users get the real voice through `/api/speech/`.
- New sections: an animated stats strip and a three-step "How it works".
- Voice cards sit in a grid, and each has a button that picks that voice in the demo and scrolls up to it.
- Logos scroll in a marquee, cards fade in as you scroll, and feature cards have a hover spotlight.
- All motion turns off when the system's reduce-motion setting is on.

### Dashboard
- A welcome banner with an animated soundwave graphic and shortcuts to Studio and Speech to Text.
- Stat cards are calculated from your real history: generations this month, characters this month, total audio length (estimated) and favourite voice.
- An activity chart shows generations per day for the last 14 days. Hover a bar to see that day's count.
- A monthly quota ring shows how much of the 10,000-character allowance is used. The sidebar bar and the "characters left" pill use the same count.
- Quick Generate offers 15 voices across several languages and sends the voice you pick.

### Studio
- The **Generate Speech** button is pinned to the bottom of the control panel, so it is always visible without scrolling.
- **Ctrl+Enter** (Cmd+Enter on Mac) generates speech from anywhere on the page.
- Fixed: the Speed and Pitch sliders now change the audio. Before, they were never sent to the backend.
- Fixed: the "pause" button inserts a plain pause (`...`) instead of an SSML tag that was read out loud. The "emphasis" button was removed for the same reason.

### New logo and favicon
- The VoiceForge logo (`frontend/assets/logo.png`) replaces the old emoji logo in the landing page header and footer, the app sidebars, and the login and register pages.
- The mic-and-face icon is the browser tab icon on every page (`frontend/favicon.ico`, `frontend/assets/favicon-32.png`) and the home-screen icon on phones (`frontend/assets/apple-touch-icon.png`).
- Both images had their backgrounds cleaned up so they sit on the dark theme without a box or halo.

### Voice cloning is hidden
- Cloning has been removed from the sidebar of every page, from the dashboard and from the landing-page pricing.
- `frontend/cloning.html` is still in the project, so the feature can be brought back later by re-adding its sidebar link.

---

## 🎛 What the Studio Does

Studio is the long-form text-to-speech editor:

1. Write or paste a script. Studio shows live character and word counts and an estimated duration.
2. Pick a language and voice (20 voices in English, Hindi, Spanish, French, German and Japanese). You can search the list or filter it by male or female voices.
3. Adjust **Speed** (0.5× to 2×) and **Pitch**.
4. Choose **MP3** or **WAV**, then click **Generate Speech** or press Ctrl+Enter.
5. Play the result and click **Export** to download it. Every clip is also saved to History.

Text sent from the Speech to Text page with **Open in Studio** lands in the editor automatically.

> Note: the **Emotion** and **Stability** controls are not used by the backend yet, so they don't change the audio.

---

## 📸 Pages

| Page | URL | Description |
|------|-----|-------------|
| Landing | `/index.html` | Marketing page with an interactive live demo |
| Login | `/login.html` | Sign in with email or Google |
| Register | `/register.html` | Create account (email or Google) |
| Dashboard | `/dashboard.html` | Welcome banner, real usage stats, activity chart, quota ring, quick generate |
| Studio | `/studio.html` | Full text-to-speech editor with a pinned Generate button |
| Speech to Text | `/transcribe.html` | Record or upload audio and get text |
| History | `/history.html` | Past generations with search |
| Voices | `/voices.html` | Browse and preview all voices |
| API | `/api.html` | API key, docs, code examples |

---

## 🏗 Tech Stack

### Backend
- **FastAPI** — REST API framework
- **Edge TTS** — Microsoft neural text-to-speech (free, 20 voices)
- **faster-whisper** — Offline speech-to-text using OpenAI's Whisper models
- **MongoDB + PyMongo** — Users, speech history and transcripts
- **bcrypt** — Password hashing
- **PyJWT** — JSON Web Token authentication
- **pydub + ffmpeg** — MP3 to WAV conversion

### Frontend
- **Vanilla HTML/CSS/JS** — No framework, no build step
- **Google Sign-In** (OAuth 2.0), verified on the backend
- **MediaRecorder API** — Microphone recording for speech to text

### Infrastructure
- **Docker + Docker Compose** — Backend, frontend and MongoDB containers
- **Nginx** — Static file server + `/api` reverse proxy
- **dev_server.py** — The same setup without Docker (serves the frontend and proxies `/api`)

---

## 📁 Project Structure

```
VoiceForge/
│
├── backend/
│   ├── app.py                  # FastAPI app entry point
│   ├── database.py             # MongoDB connection and collections
│   ├── routes/
│   │   ├── auth_routes.py      # /auth/register, /auth/login, /auth/google
│   │   ├── speech_routes.py    # /speech/ — text to speech
│   │   ├── stt_routes.py       # /stt/ — speech to text, /stt/history
│   │   └── history_routes.py   # /history/ — past generations
│   ├── services/
│   │   ├── tts_service.py      # Edge TTS voice generation
│   │   └── stt_service.py      # Whisper transcription
│   └── utils/
│       ├── auth.py             # JWT encode/decode
│       └── security.py         # Password hashing
│
├── frontend/
│   ├── index.html              # Landing page
│   ├── login.html / register.html
│   ├── dashboard.html          # Main dashboard
│   ├── studio.html             # Text-to-speech studio
│   ├── transcribe.html         # Speech to text
│   ├── history.html            # Generation history
│   ├── voices.html             # Voice library
│   ├── cloning.html            # Voice cloning (hidden, not linked anywhere)
│   ├── api.html                # API reference
│   ├── assets/                 # logo.png, favicon-32.png, apple-touch-icon.png
│   ├── favicon.ico             # Browser tab icon
│   ├── auth.js                 # Login, register, Google sign-in, logout
│   ├── ui.css                  # Shared UI polish: focus states, motion, mobile layout
│   └── ui.js                   # Mobile menu drawer, sidebar links, greeting
│
├── desktop/
│   └── tkinter_app.py          # Minimal desktop client for the API
│
├── run.py                      # Standalone desktop TTS app (gTTS, .txt/.docx)
├── dev_server.py               # Frontend server + /api proxy for running without Docker
├── generated_audio/            # Generated audio files (auto-created, git-ignored)
├── docker-compose.yml          # mongodb + backend + frontend
├── Dockerfile                  # Backend container
├── nginx.conf                  # Frontend server config
├── requirements.txt            # Python dependencies
├── .env.example                # Template for your .env (never commit .env)
├── LICENSE
└── README.md
```

---

## ⚙️ Configuration (`.env`)

Copy the template and fill it in. The same `.env` works with and without Docker.

```bash
cp .env.example .env          # Windows: copy .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` | Yes | MongoDB address when running **without** Docker, e.g. `mongodb://localhost:27017`. Docker Compose overrides it automatically. |
| `DATABASE_NAME` | Yes | Database name, e.g. `tts_db` |
| `JWT_SECRET` | Yes | Long random string used to sign login tokens |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID. Defaults to the ID in `frontend/auth.js`; set it if you use your own. |
| `STT_MODEL` | No | Speech-to-text model: `tiny`, `base` (default), `small`, `medium`, `large-v3`. Bigger is more accurate but slower. |

Example:

```env
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=tts_db
JWT_SECRET=paste-a-long-random-string-here
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
STT_MODEL=base
```

Generate a strong JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 Option 1: Run with Docker (recommended)

**You need:** Docker Desktop (running) and Git.

```bash
git clone https://github.com/yourusername/voiceforge.git
cd voiceforge
cp .env.example .env        # then edit JWT_SECRET
docker compose up --build
```

Open **http://localhost:3000**

This starts 3 containers:

| Container | Port on your PC | What it does |
|-----------|-----------------|--------------|
| `frontend` | `3000` | Nginx: serves the pages and forwards `/api/...` to the backend |
| `backend` | `8000` | FastAPI (API docs at http://localhost:8000/docs) |
| `mongodb` | `27018` | MongoDB (inside Docker the backend reaches it as `mongodb:27017`) |

ffmpeg is installed in the backend image, so WAV export works out of the box. The speech-to-text model is stored in the `whisper_models` volume, so it is only downloaded once.

### Useful Docker commands

```bash
docker compose up -d              # start in the background
docker compose down               # stop everything
docker compose up --build         # rebuild after changing requirements.txt or Dockerfile
docker compose logs -f backend    # follow backend logs
docker compose restart backend    # restart one service
docker exec -it mongodb mongosh   # open a MongoDB shell
```

---

## 💻 Option 2: Run without Docker

**You need:** Python 3.10+, MongoDB running on your PC, and optionally [ffmpeg](https://ffmpeg.org/) (only for WAV export; on Windows: `winget install ffmpeg`).

### 1. Install

```bash
python -m venv venv
# Windows (PowerShell):  venv\Scripts\Activate.ps1
# macOS / Linux:         source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
```

In `.env`, set `MONGO_URI` to your local MongoDB:
- MongoDB installed on your PC: `mongodb://localhost:27017`
- Only MongoDB from Docker (`docker compose up -d mongodb`): `mongodb://localhost:27018`

> ⚠️ Don't use `mongodb://mongodb:27017` here. That name only exists inside Docker.

### 2. Start the backend (terminal 1)

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

API docs: http://localhost:8000/docs (opening http://localhost:8000 itself shows "Not Found"; that's normal).

### 3. Start the frontend (terminal 2, from the project root)

```bash
python dev_server.py
```

Open **http://localhost:3000**

`dev_server.py` serves `frontend/` and forwards `/api/...` calls to the backend, like Nginx does in Docker. A plain `python -m http.server` won't work, because login and generation need those `/api` calls.

> After changing `.env`, stop uvicorn (Ctrl+C) and start it again. Auto-reload doesn't watch `.env`.

### Desktop app (optional)

```bash
python run.py
```
Type text or pick a `.txt` / `.docx` file to hear it read aloud. No backend or database needed.

---

## 🗣 Speech to Text

Open **Speech to Text** in the sidebar (`/transcribe.html`):

1. Pick the spoken language, or leave it on **Auto-detect**.
2. Click the microphone to record (click again to stop), **or** upload / drag in an audio file (MP3, WAV, M4A, OGG, WEBM, FLAC, up to 25 MB).
3. Edit the transcript if needed, then **Copy**, **Download .txt**, **Read aloud**, or **Open in Studio** to turn it back into speech.

Your recent transcripts are saved and listed on the same page.

**First run:** the Whisper model (`base` ≈ 150 MB) downloads automatically the first time you transcribe, so the first request takes longer. It runs fully offline on the CPU after that. Set `STT_MODEL` in `.env` to trade speed for accuracy.

**Microphone access:** browsers only allow recording on `http://localhost` or `https://` sites. Allow the microphone when the browser asks.

---

## 🔐 Google Sign-In

"Continue with Google" works on both the Login and Register pages. The browser sends Google's ID token to `POST /auth/google`, and the backend asks Google to verify it (signature, expiry, audience, issuer) and checks the one-time nonce before it creates or logs in the account. Google accounts have no password, so they can't be logged into with email/password.

To use your own Google OAuth client:
1. In Google Cloud Console, create an OAuth client ID (Web application).
2. Add **Authorized JavaScript origins:** `http://localhost:3000`
3. Add **Authorized redirect URIs:** `http://localhost:3000/login.html`
4. Put the client ID in `frontend/auth.js` (`GOOGLE_CLIENT_ID`) and in `.env` (`GOOGLE_CLIENT_ID`).

---

## 🔌 API Reference

Base URL: `http://localhost:8000` (or `http://localhost:3000/api` through the frontend). Interactive docs: http://localhost:8000/docs

### Auth

```http
POST /auth/register
Content-Type: application/json

{ "email": "you@example.com", "password": "yourpassword" }
```

```http
POST /auth/login
Content-Type: application/json

{ "email": "you@example.com", "password": "yourpassword" }

Response: { "access_token": "eyJ..." }
```

```http
POST /auth/google
Content-Type: application/json

{ "id_token": "<Google ID token>", "nonce": "<nonce sent to Google>" }

Response: { "access_token": "eyJ...", "email": "you@gmail.com" }
```

### Text to Speech

```http
POST /speech/
Authorization: Bearer <token>
Content-Type: application/json

{ "text": "Hello, world!", "voice": "aria", "speed": 1.0, "pitch": 0, "format": "mp3" }

Response: audio file (audio/mpeg or audio/wav)
```

- **voice:** any ID from the [voices table](#-available-voices)
- **format:** `mp3` or `wav` (WAV needs ffmpeg)
- **speed:** `0.5` to `2.0` (default `1.0`)
- **pitch:** `-10` to `+10` (default `0`)

### Speech to Text

```http
POST /stt/
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=<audio file>          (mp3, wav, m4a, ogg, webm, flac; max 25 MB)
language=en                (optional; leave empty to auto-detect)

Response: { "text": "Hello world", "language": "en", "duration": 2.4 }
```

```bash
curl -X POST http://localhost:8000/stt/ \
  -H "Authorization: Bearer <token>" \
  -F "file=@recording.mp3" -F "language=en"
```

### History

```http
GET /history/         # text-to-speech history
GET /stt/history      # last 50 transcripts
Authorization: Bearer <token>
```

---

## 🎙 Available Voices

| ID | Name | Gender | Language | Accent |
|----|------|--------|----------|--------|
| `aria` | Aria | Female | EN-US | American |
| `atlas` | Atlas | Male | EN-GB | British |
| `nova` | Nova | Female | EN-AU | Australian |
| `echo` | Echo | Male | EN-US | American |
| `luna` | Luna | Female | EN-US | American |
| `rex` | Rex | Male | EN-GB | British |
| `sage` | Sage | Female | EN-CA | Canadian |
| `orion` | Orion | Male | EN-AU | Australian |
| `claire` | Claire | Female | EN-US | American |
| `james` | James | Male | EN-GB | British |
| `hi_swara` | Swara | Female | HI-IN | Hindi |
| `hi_madhur` | Madhur | Male | HI-IN | Hindi |
| `es_elvira` | Elvira | Female | ES-ES | Spanish |
| `es_alvaro` | Álvaro | Male | ES-ES | Spanish |
| `fr_denise` | Denise | Female | FR-FR | French |
| `fr_henri` | Henri | Male | FR-FR | French |
| `de_katja` | Katja | Female | DE-DE | German |
| `de_konrad` | Konrad | Male | DE-DE | German |
| `ja_nanami` | Nanami | Female | JA-JP | Japanese |
| `ja_keita` | Keita | Male | JA-JP | Japanese |

---

## 🗄 Database

Collections in `DATABASE_NAME`:
- **`users`** — email plus a bcrypt password hash, or a linked Google account
- **`audio_history`** — text-to-speech requests per user
- **`transcripts`** — speech-to-text results per user

Connect with MongoDB Compass: `mongodb://localhost:27017` (local MongoDB) or `mongodb://localhost:27018` (Docker MongoDB).

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| `TypeError: name must be an instance of str, not NoneType` | `.env` is missing or not in the project root. Create it from `.env.example`. |
| `ServerSelectionTimeoutError: mongodb:27017 ... getaddrinfo failed` | Without Docker, use `MONGO_URI=mongodb://localhost:27017` (or `27018` for Docker's MongoDB). |
| `ModuleNotFoundError` when starting uvicorn | Activate the venv and run `pip install -r requirements.txt` again. |
| Login does nothing / `/api` 404 | Start the frontend with `python dev_server.py`, not `python -m http.server`. |
| `dev_server.py` says "Backend not reachable" | Start uvicorn on port 8000 first. |
| `Couldn't find ffmpeg` warning | Only needed for WAV. Install ffmpeg, or use MP3. |
| Speech to text is slow the first time | The Whisper model is downloading. Later requests are faster. |
| Microphone button shows "access was blocked" | Allow the microphone for `localhost:3000` in your browser's site settings. |

---

## 🔐 Security Notes

- Passwords hashed with **bcrypt** (cost factor 12)
- Google sign-in tokens are verified by the backend before any account is created or logged in
- JWT tokens signed with HS256 and expire after 24 hours
- API routes require an `Authorization: Bearer <token>` header
- MongoDB runs without auth in development; add auth for production
- Never commit your `.env` file (it's already in `.gitignore`)

---

## 🌐 Production Deployment

1. **`.env`:** use a hosted database and a strong secret
   ```env
   MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net
   JWT_SECRET=<64-char random string>
   ```
   With Docker, also remove the `MONGO_URI` line under `backend: environment:` in `docker-compose.yml` so your `.env` value is used.
2. **`nginx.conf`:** set `server_name yourdomain.com www.yourdomain.com;`
3. **SSL:** `certbot --nginx -d yourdomain.com`
4. **Google OAuth:** add `https://yourdomain.com` to Authorized JavaScript origins and `https://yourdomain.com/login.html` to redirect URIs.

| Service | What for | Cost |
|---------|----------|------|
| Railway / Render | Backend (FastAPI) | Free tier |
| Vercel / Netlify | Frontend (static) | Free |
| MongoDB Atlas | Database | Free 512MB |
| Cloudflare R2 | Audio file storage | Free 10GB |

---

## 📈 Roadmap

- [x] Speech to text
- [x] Verified Google sign-in
- [ ] Stripe subscription billing
- [ ] Real voice cloning (Pro)
- [ ] SSML support
- [ ] Audio storage on S3/R2
- [ ] Team workspaces
- [ ] Mobile app

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit: `git commit -m 'Add your feature'`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Built with FastAPI · Edge TTS · faster-whisper · MongoDB · Docker · Nginx
