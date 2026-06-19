# Pemdi RAG Agent

Sistem *Retrieval-Augmented Generation* (RAG) cerdas yang dirancang untuk menganalisis dan menjawab pertanyaan seputar "Indeks Pemdi" berdasarkan dokumen pedoman yang terindeks secara otomatis.

Aplikasi ini dibangun dengan *stack* modern:
- **FastAPI** (Backend Framework)
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
   - Melakukan *build* pada aplikasi FastAPI.
   - Mengunduh model *embedding* `intfloat/multilingual-e5-base` (hanya pada saat *run* pertama).
   - Memotong (*chunking*) dan memproses file PDF yang belum terindeks ke dalam Vector DB.

3. **Cek Log Aplikasi**
   Untuk memastikan bahwa RAG Agent sudah menyala dan index sudah selesai:
   ```bash
   docker compose logs -f app
   ```
   Tunggu hingga muncul pesan `Uvicorn running on http://0.0.0.0:8080`.

## Dokumentasi API (Swagger UI)

Aplikasi ini berjalan pada Port `8080` secara bawaan. Anda bisa mengakses dokumentasi interaktif (Swagger UI) secara otomatis pada:
👉 **[http://localhost:8080/docs](http://localhost:8080/docs)**

## Endpoint Utama

### 1. Chat (LangGraph RAG Agent)
- `POST /chat`
- Digunakan untuk melakukan obrolan dengan agen cerdas terkait dokumen Pemdi.
**Contoh Payload:**
```json
{
  "message": "Apa saja aspek penilaian dalam Indeks Pemdi?",
  "session_id": "user-session-123"
}
```

### 2. Root & Health Check
- `GET /` : Menampilkan pesan selamat datang.
- `GET /health` : Mengecek status aplikasi dan jumlah dokumen PDF (chunks) yang telah berhasil diindeks ke database vektor ChromaDB.

### 3. Calculate Index (Tool Manual)
- `POST /calculate-index`
- Digunakan untuk menghitung nilai Indeks secara spesifik/manual berdasarkan input dari Frontend tanpa perlu obrolan AI panjang.

## Struktur Direktori Utama
- `app/` : *Source code* utama aplikasi Python (FastAPI, agent.py, rag.py, dll).
- `data/` : Folder wajib untuk menyimpan file dokumen PDF.
- `.env` : File rahasia yang tidak di-push ke Github.
- `docker-compose.yml` : Konfigurasi orkestrasi container backend & database.

## Catatan Arsitektur
Sistem ini secara khusus dirancang menggunakan pendekatan **JSON ReAct Parser** pada agen LangGraph. Teknik *prompting* tingkat lanjut ini digunakan untuk menjembatani kompatibilitas antara format standar bawaan Langchain dengan model Open-Source TokenRouter (seperti MiniMax-M3) yang restriktif terhadap skema JSON Tool-Calling konvensional.
