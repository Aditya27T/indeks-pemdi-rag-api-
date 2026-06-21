# Pemdi RAG Agent & Web Interface

Sistem *Retrieval-Augmented Generation* (RAG) cerdas yang dirancang untuk menganalisis dan menjawab pertanyaan seputar "Indeks Pemdi" berdasarkan dokumen pedoman yang terindeks secara otomatis. Dilengkapi dengan antarmuka web interaktif yang mewah dan dibangun dalam satu image Docker.

Aplikasi ini dibangun dengan *stack* modern:
- **FastAPI** (Backend API Framework)
- **Svelte & Vite** (Frontend Web UI - Multi-stage Build)
- **LangGraph** (Stateful Agent Orchestration)
- **LangChain** (RAG & Tooling)
- **ChromaDB** (Vector Database)
- **Docker Compose** (Containerization)
- **MiniMax-M3 via TokenRouter** (LLM Provider)

## Prasyarat
- Docker dan Docker Compose telah terinstall di mesin Anda.
- File PDF pedoman (misal: `2026permenpanrb008.pdf`) yang diletakkan pada folder `/data`.

## Instalasi & Menjalankan Proyek

1. **Persiapkan Variabel Lingkungan (Environment Variables)**
   Salin `.env.example` menjadi `.env` lalu sesuaikan isinya:
   ```bash
   cp .env.example .env
   ```
   *Penting: Isi `TOKENROUTER_API_KEY` dengan API Key TokenRouter yang Anda miliki sebelum melanjutkan.*

2. **Jalankan Aplikasi dengan Docker Compose**
   ```bash
   docker compose up -d --build
   ```
   *Perintah di atas akan secara otomatis:*
   - Menjalankan instance ChromaDB secara persisten.
   - Melakukan *build* Svelte Frontend (Node.js).
   - Melakukan *build* aplikasi backend FastAPI sekaligus menyematkan UI (*multi-stage build*).
   - Mengunduh model *embedding* `intfloat/multilingual-e5-base` (hanya pada saat *run* pertama).
   - Memotong (*chunking*) dan memproses file PDF yang belum terindeks ke dalam Vector DB.

3. **Buka Aplikasi (Frontend Web)**
   Kini Anda tidak hanya bisa mengakses API, tetapi juga UI interaktif! Buka browser Anda pada:
   👉 **[http://localhost:8080/](http://localhost:8080/)**

   Di sana Anda akan menemukan:
   - **Menu Chatbot**: Layar obrolan gaya LLM dengan dukungan Markdown dan anotasi referensi sumber halaman.
   - **Menu Kalkulator**: Antarmuka untuk menghitung otomatis skor Indeks Pemdi Anda secara instan dari 20 indikator yang ada.

## Dokumentasi API (Swagger UI)

Anda bisa tetap mengakses dokumentasi interaktif API backend (Swagger UI) secara otomatis pada:
👉 **[http://localhost:8080/docs](http://localhost:8080/docs)**

## Endpoint Backend Utama

### 1. Chat (LangGraph RAG Agent)
- `POST /chat`
- Digunakan untuk melakukan obrolan dengan agen cerdas terkait dokumen Pemdi.

### 2. Status & Health Check
- `GET /health` : Mengecek status aplikasi dan jumlah dokumen PDF (chunks) yang telah berhasil diindeks ke database vektor ChromaDB.
- `GET /` : *Diarahkan ke File Svelte Web UI.*

### 3. Calculate Index
- `POST /calculate-index`
- Digunakan untuk menghitung nilai Indeks secara matematis berdasarkan input indikator Pemdi.

## Struktur Direktori Utama
- `app/` : *Source code* utama aplikasi Python dan Dockerfile Multi-Stage.
  - `app/frontend/` : *Source code* Frontend (Svelte + Vite) dengan komponen terpisah.
- `data/` : Folder wajib untuk menyimpan file dokumen PDF.
- `.env` : File rahasia konfigurasi server.
- `docker-compose.yml` : Konfigurasi orkestrasi container backend & database.

## Catatan Arsitektur
Sistem ini memadukan **Single Docker Image** untuk Frontend (SPA) dan Backend (API). Proses build memanfaatkan Node.js (untuk compile Svelte) lalu dicopy ke container Python FastAPI untuk di-*serve* pada root (`/`). Agen LangGraph juga dibangun menggunakan **JSON ReAct Parser** untuk kompatibilitas LLM MiniMax-M3 yang sangat tangguh di Bahasa Indonesia.
