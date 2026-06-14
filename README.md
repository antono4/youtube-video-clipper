# YouTube Video Clipper

Aplikasi web untuk mengekstrak dan mengunduh bagian spesifik dari video YouTube dalam format MP4.

![YouTube Clipper](https://img.shields.io/badge/YouTube-Clipper-red)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-CSS-38B2AC)

## ✨ Fitur

- **Input URL YouTube** - Validasi dan ekstrak informasi video
- **Video Preview** - Tonton video langsung di browser
- **Timeline Clipper** - Pilih segment waktu dengan slider interaktif
- **Stream Processing** - Hemat bandwidth dengan FFmpeg streaming
- **Download MP4** - Unduh hasil klip langsung ke perangkat
- **🔗 URL Shortener** - Pendekatkan link download dengan Shrtco.de API
- **☁️ Cloud Upload** - Upload clip ke GoFile.io cloud storage
- **📊 Video Metadata** - Ambil data tambahan video dari YouTube
- **📈 Clip Statistics** - Lihat statistik clip yang dibuat

## 🛠️ Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Backend | Python 3.10+ (FastAPI) |
| Frontend | HTML5, Tailwind CSS, Vanilla JS |
| Video Processing | yt-dlp, FFmpeg |
| Server | Uvicorn (ASGI) |

## 📁 Struktur Proyek

```
youtube-clipper/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── api/
│   │   ├── routes.py        # API endpoints
│   │   └── schemas.py       # Pydantic models
│   ├── core/
│   │   ├── config.py        # App configuration
│   │   └── exceptions.py    # Custom exceptions
│   ├── services/
│   │   └── video_service.py # Video processing logic
│   └── utils/
│       └── helpers.py       # Utility functions
├── frontend/
│   ├── index.html           # Main HTML file
│   ├── css/
│   │   └── styles.css       # Custom styles
│   └── js/
│       ├── app.js           # Main application logic
│       ├── api.js           # API communication
│       ├── video-player.js  # YouTube player controller
│       └── timeline.js      # Timeline slider controller
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🚀 Instalasi

### Prasyarat

- Python 3.10 atau lebih baru
- FFmpeg terinstall di sistem
- pip (Python package manager)

### Langkah 1: Clone Repository

```bash
git clone https://github.com/yourusername/youtube-clipper.git
cd youtube-clipper
```

### Langkah 2: Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download dari https://ffmpeg.org/download.html dan tambahkan ke PATH.

### Langkah 3: Buat Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# atau
venv\Scripts\activate  # Windows
```

### Langkah 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Langkah 5: Jalankan Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Langkah 6: Buka Frontend

Buka file `frontend/index.html` di browser, atau gunakan static server:

```bash
# Dengan Python
cd ../frontend
python -m http.server 3000

# Atau dengan npx
npx http-server -p 3000
```

Buka http://localhost:3000 di browser.

## 🐳 Docker Deployment

### Build dan Jalankan

```bash
docker-compose up --build
```

Aplikasi akan tersedia di:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Stop Containers

```bash
docker-compose down
```

## 📡 API Reference

### POST /api/validate

Validasi URL YouTube dan dapatkan informasi video.

```bash
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

**Response:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "duration": 213,
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "uploader": "Rick Astley",
  "description": "The official video for..."
}
```

### POST /api/process

Proses klip video.

```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "start_time": 30,
    "end_time": 60
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Clip berhasil dibuat!",
  "file_path": "/api/download/abc123-def456",
  "file_size": 5242880,
  "session_id": "abc123-def456"
}
```

### GET /api/download/{session_id}

Download file klip.

```bash
curl -O http://localhost:8000/api/download/abc123-def456
```

### POST /api/shorten

Pendekatkan URL download menggunakan Shrtco.de API.

```bash
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/api/download/abc123"}'
```

**Response:**
```json
{
  "success": true,
  "original_url": "https://example.com/api/download/abc123",
  "short_url": "https://shrtco.de/xyz",
  "short_url_2": "https://shrtco.de/abc",
  "share_url": "https://shrtco.de/share/xyz"
}
```

### GET /api/thumbnail/{video_id}

Dapatkan thumbnail video YouTube.

```bash
curl http://localhost:8000/api/thumbnail/dQw4w9WgXcQ
```

**Response:**
```json
{
  "success": true,
  "video_id": "dQw4w9WgXcQ",
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "thumbnails": {
    "maxresdefault": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
    "hqdefault": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
  }
}
```

### POST /api/upload

Upload clip ke GoFile.io cloud storage.

```bash
curl -X POST http://localhost:8000/api/upload \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123-def456"}'
```

**Response:**
```json
{
  "success": true,
  "download_page": "https://gofile.io/d/abc123",
  "direct_link": "https://store1.gofile.io/contents/download/abc123.mp4",
  "file_name": "clip_abc123-def456.mp4"
}
```

### GET /api/metadata/{video_id}

Dapatkan metadata tambahan video YouTube.

```bash
curl http://localhost:8000/api/metadata/dQw4w9WgXcQ
```

**Response:**
```json
{
  "success": true,
  "author_name": "Rick Astley",
  "author_url": "https://www.youtube.com/@RickAstley",
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
}
```

### GET /api/stats/{session_id}

Dapatkan statistik clip yang telah diproses.

```bash
curl http://localhost:8000/api/stats/abc123-def456
```

**Response:**
```json
{
  "success": true,
  "session_id": "abc123-def456",
  "clip_duration": 30,
  "clip_size": 5242880,
  "created_at": "2024-01-01T00:00:00",
  "file_path": "/tmp/youtube-clipper/abc123-def456/output.mp4"
}
```

## ⚙️ Konfigurasi

Buat file `.env` di folder `backend/`:

```env
# Application
APP_NAME=YouTube Video Clipper
DEBUG=false

# Limits
MAX_CLIP_DURATION=300  # 5 minutes
MAX_FILE_SIZE=524288000  # 500MB

# Video Settings
VIDEO_CODEC=libx264
AUDIO_CODEC=aac
AUDIO_BITRATE=128k
```

## 🔒 Keamanan

- File temporary dihapus otomatis setelah download
- CORS dikonfigurasi untuk mencegah akses tidak sah
- Validasi input yang ketat untuk mencegah injection
- Batasan ukuran dan durasi untuk mencegah abuse

## ⚠️ Batasan

- Durasi klip maksimal: 5 menit
- Ukuran file maksimal: 500MB
- Hanya video yang publicly available
- Patuhi Terms of Service YouTube

## 🐛 Troubleshooting

| Error | Solusi |
|-------|--------|
| `ffmpeg: command not found` | Install FFmpeg |
| `Video is private` | Gunakan video yang publicly available |
| `CORS error` | Pastikan backend dan frontend berjalan di port yang benar |

## 📄 License

MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan buat pull request atau buka issue.

---

Dibuat dengan ❤️ menggunakan FastAPI, Tailwind CSS, yt-dlp, dan FFmpeg