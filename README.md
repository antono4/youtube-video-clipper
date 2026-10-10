<h1 align="center">🎬 YouTube Video Clipper</h1>

<p align="center">
  <strong>Ekstrak dan unduh potongan video dari YouTube dalam format MP4</strong>
</p>

<p align="center">
  <a href="https://github.com/antono4/youtube-video-clipper"><img alt="GitHub repo" src="https://img.shields.io/badge/GitHub-antono4/youtube-video-clipper-blue?logo=github"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

---

## 📖 Tentang

**YouTube Video Clipper** adalah aplikasi web untuk mengunduh video YouTube berdasarkan URL, memilih segmen waktu tertentu (start & end), lalu memotongnya menjadi klip MP4 yang bisa langsung diunduh. Backend dibangun dengan **FastAPI** dan proses video memakai **yt-dlp** + **FFmpeg**, sedangkan frontend adalah halaman statis berbasis **Tailwind CSS** dan Vanilla JS.

## ✨ Fitur

- **Input URL YouTube** — mendukung format `watch?v=`, `youtu.be`, `embed`, dan `shorts`.
- **Pratinjau video** — menampilkan judul, durasi, thumbnail, dan uploader sebelum memotong.
- **Pemilih timeline** — menentukan waktu mulai & selesai klip secara interaktif.
- **Proses klip** — memotong video memakai FFmpeg dan menghasilkan file MP4 (H.264/AAC).
- **Unduh MP4** — mengunduh hasil klip melalui endpoint download per sesi.
- **Thumbnail YouTube** — mengambil thumbnail berbagai kualitas (`maxresdefault`, `hqdefault`, `mqdefault`, `sddefault`).
- **Upload ke cloud** — mengunggah hasil klip ke GoFile.io dan membagikan halaman download.
- **Short link** — memendekkan URL berbagi klip.
- **Metadata video** — mengambil metadata tambahan (author, dimensi, HTML embed).
- **Bersih-bersih otomatis** — menghapus file sesi sementara melalui endpoint cleanup.

## 🛠️ Teknologi

| Layer | Teknologi |
|-------|-----------|
| Backend | Python 3.10+ (FastAPI, Uvicorn) |
| Pemrosesan video | yt-dlp + FFmpeg (moviepy) |
| Frontend | HTML5, Tailwind CSS (CDN), Vanilla JS |
| Konfigurasi | pydantic-settings |
| Kontainer | Docker & Docker Compose |
| Web server (frontend) | Nginx |

## 🏗️ Arsitektur

```
Browser (frontend/)
        │  HTTP / REST
        ▼
Nginx (port 80)  ──proxy /api/──▶  FastAPI backend (port 8000)
                                        │
                                        ▼
                        yt-dlp (unduh) + FFmpeg (potong)
                                        │
                                        ▼
                     /tmp/youtube-clipper/{session_id}/output.mp4
```

## 🗂️ Struktur Proyek

```
youtube-video-clipper/
├── backend/                  # FastAPI backend
│   ├── main.py               # Entry point aplikasi
│   ├── requirements.txt      # Dependensi Python
│   ├── Dockerfile            # Image backend (Python + FFmpeg)
│   ├── .env.example          # Template konfigurasi
│   ├── api/                  # Route & skema (routes.py, schemas.py)
│   ├── core/                 # Konfigurasi & exception (config.py, exceptions.py)
│   ├── services/             # Logika bisnis (video_service.py, external_services.py)
│   ├── utils/                # Helper (helpers.py)
│   └── tests/                # Unit test (pytest)
├── frontend/                 # Frontend versi lengkap (Tailwind + fitur cloud/short link)
│   ├── index.html
│   ├── css/styles.css
│   └── js/                   # app.js, api.js, timeline.js, video-player.js
├── docs/                     # Versi demo untuk GitHub Pages
├── temp/                     # Penyimpanan file sementara
├── nginx.conf                # Konfigurasi reverse proxy Nginx
├── docker-compose.yml        # Orkestrasi backend + frontend
├── BLUEPRINT.md              # Blueprint arsitektur
└── TEST_REPORT.md            # Laporan pengujian
```

> **Catatan:** folder `docs/` dan `frontend/` berisi halaman yang hampir sama. `frontend/` adalah versi terlengkap (termasuk tombol *Upload ke Cloud* dan *Salin Link*), sedangkan `docs/` adalah versi yang dipublikasikan sebagai demo statis melalui GitHub Pages.

## 🔌 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET`  | `/` | Info aplikasi |
| `GET`  | `/health` | Health check |
| `POST` | `/api/validate` | Validasi URL & ambil info video |
| `POST` | `/api/process` | Proses pemotongan klip |
| `GET`  | `/api/download/{session_id}` | Unduh hasil klip (MP4) |
| `DELETE` | `/api/cleanup/{session_id}` | Hapus file sesi |
| `POST` | `/api/shorten` | Memendekkan URL |
| `GET`  | `/api/thumbnail/{video_id}` | Ambil URL thumbnail |
| `POST` | `/api/upload` | Upload klip ke GoFile.io |
| `GET`  | `/api/metadata/{video_id}` | Metadata tambahan video |
| `GET`  | `/api/stats/{session_id}` | Statistik klip |

Dokumentasi interaktif (Swagger) tersedia di `/docs` dan ReDoc di `/redoc` saat backend berjalan.

## 🚀 Menjalankan Secara Lokal

### Opsi 1 — Docker Compose (disarankan)

Cara paling mudah karena FFmpeg sudah terpasang di image backend.

```bash
docker compose up --build
# Frontend: http://localhost
# Backend : http://localhost:8000  (docs: http://localhost:8000/docs)
```

### Opsi 2 — Manual

Prasyarat: **Python 3.10+** dan **FFmpeg** terpasang di sistem.

```bash
# 1. Buat virtual environment & install dependensi
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. (Opsional) salin template konfigurasi
cp .env.example .env

# 3. Jalankan backend
uvicorn main:app --reload --port 8000
```

Lalu jalankan frontend dengan server statis:

```bash
# dari root repository
python3 -m http.server 3000 --directory frontend
# buka http://localhost:3000
```

Frontend mendeteksi API di `http://<host>:8000` secara otomatis saat port bernilai `3000`, `80`, atau kosong.

## ⚙️ Konfigurasi

Konfigurasi dibaca dari variabel lingkungan (lihat `backend/.env.example`):

| Variabel | Default | Deskripsi |
|----------|---------|-----------|
| `APP_NAME` | `YouTube Video Clipper` | Nama aplikasi |
| `APP_VERSION` | `1.0.0` | Versi aplikasi |
| `DEBUG` | `false` | Mode debug |
| `TEMP_DIR` | `/tmp/youtube-clipper` | Direktori file sementara |
| `MAX_CLIP_DURATION` | `300` | Durasi klip maksimum (detik) |
| `MAX_FILE_SIZE` | `524288000` | Ukuran file maksimum (byte) |
| `OUTPUT_FORMAT` | `mp4` | Format keluaran |
| `VIDEO_CODEC` | `libx264` | Codec video |
| `AUDIO_CODEC` | `aac` | Codec audio |
| `AUDIO_BITRATE` | `128k` | Bitrate audio |
| `CORS_ORIGINS` | `*` | Origin CORS yang diizinkan |

## 🧪 Pengujian

```bash
cd backend
pip install -r requirements.txt
pytest
```

Suite pengujian mencakup validasi skema, endpoint API, dan fitur tambahan (51 test). Lihat [`TEST_REPORT.md`](./TEST_REPORT.md) untuk laporan lengkap.

## 🌐 Demo

Versi statis frontend dipublikasikan melalui GitHub Pages di
[https://antono4.github.io/youtube-video-clipper/docs/](https://antono4.github.io/youtube-video-clipper/docs/).
Demo ini hanya menampilkan antarmuka; pemrosesan video tetap memerlukan backend yang berjalan.

## 📬 Kontak

- GitHub: [antono4](https://github.com/antono4)

## 📄 Lisensi

Proyek ini dilisensikan di bawah MIT — lihat berkas [`LICENSE`](./LICENSE) untuk detail.
