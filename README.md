<!-- README ini dihasilkan otomatis oleh .github/workflows/generate-readme.yml -->
<!-- Jangan edit manual: perubahan akan ditimpa pada run berikutnya. -->

<h1 align="center">youtube-video-clipper 👋</h1>

<p align="center">
  <em>YouTube Video Clipper - Blueprint arsitektur lengkap</em>
</p>

<p align="center">
  <a href="https://github.com/antono4/youtube-video-clipper"><img alt="GitHub repo" src="https://img.shields.io/badge/GitHub-antono4/youtube-video-clipper-blue?logo=github"></a>
  <a href="https://antono4.github.io/youtube-video-clipper/"><img alt="Live Demo" src="https://img.shields.io/badge/Live%20Demo-Online-success?logo=githubpages"></a>
  <img alt="Files" src="https://img.shields.io/badge/Files-34-informational">
  <img alt="Last commit" src="https://img.shields.io/github/last-commit/antono4/youtube-video-clipper">
</p>

---

## 📖 Tentang

Repository **`youtube-video-clipper`** adalah proyek Python yang dibangun dengan HTML, CSS, JavaScript, Python.
Demo berjalan tersedia melalui **GitHub Pages** di [`https://antono4.github.io/youtube-video-clipper/`](https://antono4.github.io/youtube-video-clipper/).

## 🗂️ Struktur Proyek

```
youtube-video-clipper/
.github/
  workflows/
BLUEPRINT.md
LICENSE
backend/
  .env.example
  Dockerfile
  __init__.py
  api/
  core/
  main.py
  requirements.txt
  services/
  utils/
docker-compose.yml
docs/
  .nojekyll
  css/
  index.html
  js/
frontend/
  css/
  index.html
  js/
nginx.conf
temp/
  .gitkeep
```

## 🌐 Sub-Proyek / Demo

Repository ini juga memuat sub-proyek (masing-masing punya `index.html` tersendiri):

| Folder | Keterangan |
|--------|-----------|
| [`docs`](./docs) | YouTube Video Clipper | Extract & Download Video Clips |
| [`frontend`](./frontend) | YouTube Video Clipper | Extract & Download Video Clips |

## 🛠️ Teknologi

Berdasarkan ekstensi berkas yang terdeteksi di repository:

- `HTML`
- `CSS`
- `JavaScript`
- `Python`

> Total **34 berkas** di repository (di luar `.git`, `node_modules`, `dist`, dan `build`).

## 🚀 Menjalankan Secara Lokal

Butuh Python 3:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 📬 Kontak

- GitHub: [antono4](https://github.com/antono4)

## 📄 Lisensi

Proyek ini dilisensikan di bawah MIT License — lihat berkas [`LICENSE`](./LICENSE).

---

<sub>README ini di-generate otomatis oleh GitHub Actions `.github/workflows/generate-readme.yml`.</sub>
