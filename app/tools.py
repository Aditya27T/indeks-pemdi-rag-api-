from langchain_core.tools import tool
from typing import Dict, Any

@tool
def calculate_pemdi_index(indicators: Dict[str, float]) -> Dict[str, Any]:
    """
    Hitung Indeks Pemdi sesuai formula di PermenPANRB No.8/2026.
    Input adalah dictionary berisi nilai per indikator (float 1.0-5.0).
    Output adalah indeks total, predikat, dan breakdown per aspek.
    
    Daftar kunci (keys) indikator yang diharapkan:
    - Aspek 1 (Tata Kelola dan Manajemen): tata_kelola, manajemen_layanan, sdm, kolaborasi
    - Aspek 2 (Penyelenggara): tata_kelola_data, geospasial, statistik
    - Aspek 3 (Data): pdp
    - Aspek 4 (Keamanan Pemdi): audit_keamanan, keamanan_pemdi, kriptografi, insiden_siber
    - Aspek 5 (Teknologi Pemdi): aplikasi, infrastruktur
    - Aspek 6 (Keterpaduan Layanan Digital): proses_bisnis, integrasi_aplikasi, portal, interoperabilitas
    - Aspek 7 (Kepuasan Pengguna): dukungan_pengguna, kepuasan_pengguna
    """
    
    # Aspek 1: Tata Kelola dan Manajemen (Bobot: 10%)
    aspek1 = (indicators.get("tata_kelola", 0) + indicators.get("manajemen_layanan", 0) + 
              indicators.get("sdm", 0) + indicators.get("kolaborasi", 0)) / 4
              
    # Aspek 2: Penyelenggara (Bobot: 10%)
    aspek2 = (indicators.get("tata_kelola_data", 0) + indicators.get("geospasial", 0) + 
              indicators.get("statistik", 0)) / 3
              
    # Aspek 3: Data (Bobot: 15%)
    aspek3 = indicators.get("pdp", 0)
    
    # Aspek 4: Keamanan Pemdi (Bobot: 15%)
    aspek4 = (indicators.get("audit_keamanan", 0) + indicators.get("keamanan_pemdi", 0) + 
              indicators.get("kriptografi", 0) + indicators.get("insiden_siber", 0)) / 4
              
    # Aspek 5: Teknologi Pemdi (Bobot: 10%)
    aspek5 = (indicators.get("aplikasi", 0) + indicators.get("infrastruktur", 0)) / 2
    
    # Aspek 6: Keterpaduan Layanan Digital (Bobot: 15%)
    aspek6 = (indicators.get("proses_bisnis", 0) + indicators.get("integrasi_aplikasi", 0) + 
              indicators.get("portal", 0) + indicators.get("interoperabilitas", 0)) / 4
              
    # Aspek 7: Kepuasan Pengguna (Bobot: 25%)
    aspek7 = (indicators.get("dukungan_pengguna", 0) + indicators.get("kepuasan_pengguna", 0)) / 2
    
    indeks_pemdi = (aspek1 * 0.10) + (aspek2 * 0.10) + (aspek3 * 0.15) + \
                   (aspek4 * 0.15) + (aspek5 * 0.10) + (aspek6 * 0.15) + (aspek7 * 0.25)
                   
    # Predikat (Berdasarkan nilai 1-5, ini asumsi umum untuk kategori 1-5)
    predikat = "Memuaskan"
    if indeks_pemdi < 1.5:
        predikat = "Sangat Kurang/Perlu Perbaikan"
    elif indeks_pemdi < 2.5:
        predikat = "Kurang/Mulai Berkembang"
    elif indeks_pemdi < 3.5:
        predikat = "Baik/Berkembang/Developing"
    elif indeks_pemdi < 4.5:
        predikat = "Sangat Baik"
    
    return {
        "indeks_pemdi": round(indeks_pemdi, 2),
        "predikat": predikat,
        "detail_aspek": {
            "Tata Kelola dan Manajemen": round(aspek1, 2),
            "Penyelenggara": round(aspek2, 2),
            "Data": round(aspek3, 2),
            "Keamanan Pemdi": round(aspek4, 2),
            "Teknologi Pemdi": round(aspek5, 2),
            "Keterpaduan Layanan Digital": round(aspek6, 2),
            "Kepuasan Pengguna": round(aspek7, 2)
        }
    }

@tool
def list_aspects() -> str:
    """
    Tampilkan semua aspek evaluasi Pemdi dan bobotnya.
    """
    return '''Daftar Aspek dan Bobot pada Evaluasi Kinerja Pemdi:
1. Tata Kelola dan Manajemen (10%, 4 indikator)
2. Penyelenggara (10%, 3 indikator)
3. Data (15%, 1 indikator)
4. Keamanan Pemdi (15%, 4 indikator)
5. Teknologi Pemdi (10%, 2 indikator)
6. Keterpaduan Layanan Digital (15%, 4 indikator)
7. Kepuasan Pengguna (25%, 2 indikator)
'''

@tool
def search_pemdi_doc(query: str) -> str:
    """
    Cari informasi relevan dari dokumen PermenPANRB No.8/2026.
    Gunakan tool ini ketika perlu menjawab pertanyaan berdasarkan isi dokumen.
    """
    from rag import get_retriever
    retriever = get_retriever()
    
    # multilingual-e5-base works best with query prefix
    prefixed_query = f"query: {query}"
    docs = retriever.invoke(prefixed_query)
    
    res = []
    for doc in docs:
        page = doc.metadata.get("page", "?")
        # Remove "passage: " prefix if exists for display
        content = doc.page_content.replace("passage: ", "")
        res.append(f"[Halaman {page}]\n{content}")
        
    return "\n\n---\n\n".join(res)
