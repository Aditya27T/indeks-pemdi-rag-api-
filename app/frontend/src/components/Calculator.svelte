<script>
  let indicators = {
    tata_kelola: 3.0, manajemen_layanan: 3.0, sdm: 3.0, kolaborasi: 3.0,
    tata_kelola_data: 3.0, geospasial: 3.0, statistik: 3.0, pdp: 3.0,
    audit_keamanan: 3.0, keamanan_pemdi: 3.0, kriptografi: 3.0, insiden_siber: 3.0,
    aplikasi: 3.0, infrastruktur: 3.0, proses_bisnis: 3.0, integrasi_aplikasi: 3.0,
    portal: 3.0, interoperabilitas: 3.0, dukungan_pengguna: 3.0, kepuasan_pengguna: 3.0
  };
  let calcResult = null;
  let isCalcLoading = false;

  export let isActive = false;

  async function calculateIndex() {
    isCalcLoading = true;
    try {
      const res = await fetch('/calculate-index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ indicators })
      });
      calcResult = await res.json();
    } catch (e) {
      alert('Gagal menghitung indeks.');
    } finally {
      isCalcLoading = false;
    }
  }
</script>

<div class="calculator-container" style="display: {isActive ? 'block' : 'none'}">
  <h2>Kalkulator Indeks Pemdi</h2>
  <p>Masukkan nilai indikator (1.0 - 5.0)</p>
  <div class="form-grid">
    {#each Object.keys(indicators) as key}
      <div class="form-group">
        <label>{key.replace(/_/g, ' ').toUpperCase()}</label>
        <input type="number" min="1" max="5" step="0.1" bind:value={indicators[key]} />
      </div>
    {/each}
  </div>
  <button class="calc-btn" on:click={calculateIndex} disabled={isCalcLoading}>
    {isCalcLoading ? 'Menghitung...' : 'Hitung Indeks'}
  </button>

  {#if calcResult}
    <div class="result-card">
      <h3>Hasil Evaluasi: {calcResult.predikat}</h3>
      <div class="score">{calcResult.indeks_pemdi.toFixed(2)}</div>
      <div class="aspects">
        {#each Object.entries(calcResult.detail_aspek) as [aspek, nilai]}
          <div class="aspect-row">
            <span>{aspek}</span>
            <strong>{Number(nilai).toFixed(2)}</strong>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>
