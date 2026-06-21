<script>
  import { useCalculator } from '../hooks/useCalculator.js';
  import { useChat } from '../hooks/useChat.js';
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';
  import Chart from 'chart.js/auto';

  export let isActive = false;

  const { isLoading, result, calculateIndex } = useCalculator();
  const indexChat = useChat();
  let chatInput = '';
  
  let indicators = {
    tata_kelola: 3.0, manajemen_layanan: 3.0, sdm: 3.0, kolaborasi: 3.0,
    tata_kelola_data: 3.0, geospasial: 3.0, statistik: 3.0, pdp: 3.0,
    audit_keamanan: 3.0, keamanan_pemdi: 3.0, kriptografi: 3.0, insiden_siber: 3.0,
    aplikasi: 3.0, infrastruktur: 3.0, proses_bisnis: 3.0, integrasi_aplikasi: 3.0,
    portal: 3.0, interoperabilitas: 3.0, dukungan_pengguna: 3.0, kepuasan_pengguna: 3.0
  };

  function handleCalculate() {
    calculateIndex(indicators);
    indexChat.clearChat(); // Reset chat when recalculating
  }

  function handleChatSend() {
    if (!chatInput.trim()) return;
    
    let payload = chatInput;
    if ($indexChat.messages.length === 1 && $result) {
      const res = $result;
      const rincian = Object.entries(res.detail_aspek).map(([k, v]) => `${k} (${v.toFixed(2)})`).join(', ');
      payload = `Hasil evaluasi saya: Nilai ${res.indeks_pemdi.toFixed(2)}, Predikat ${res.predikat}. Rincian: ${rincian}.\n\nPertanyaan: ${chatInput}`;
    }

    indexChat.sendMessage(payload);
    chatInput = '';
  }

  function handleChatKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleChatSend();
    }
  }

  function parseMarkdown(text) {
    if (!text) return '';
    return DOMPurify.sanitize(marked.parse(text));
  }

  function renderRadarChart(node, dataResult) {
    if (!dataResult) return;
    
    const chart = new Chart(node, {
      type: 'radar',
      data: {
        labels: Object.keys(dataResult.detail_aspek),
        datasets: [{
          label: 'Skor Aspek',
          data: Object.values(dataResult.detail_aspek).map(v => Number(v.toFixed(2))),
          backgroundColor: 'rgba(16, 163, 127, 0.3)',
          borderColor: 'rgba(16, 163, 127, 1)',
          pointBackgroundColor: 'rgba(16, 163, 127, 1)',
          pointBorderColor: '#fff',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
            grid: { color: 'rgba(255, 255, 255, 0.1)' },
            pointLabels: { color: '#ececec', font: { size: 11, family: 'Inter' } },
            ticks: { display: false, min: 0, max: 5, stepSize: 1 }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });

    return {
      update(newData) {
        if(!newData) return;
        chart.data.labels = Object.keys(newData.detail_aspek);
        chart.data.datasets[0].data = Object.values(newData.detail_aspek).map(v => Number(v.toFixed(2)));
        chart.update();
      },
      destroy() {
        chart.destroy();
      }
    };
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
  <button class="calc-btn" on:click={handleCalculate} disabled={$isLoading}>
    {$isLoading ? 'Menghitung...' : 'Hitung Indeks'}
  </button>

  {#if $result}
    <div class="result-card">
      <h3>Hasil Evaluasi: {$result.predikat}</h3>
      <div class="score">{$result.indeks_pemdi.toFixed(2)}</div>
      
      <div class="result-details" style="display: flex; gap: 30px; flex-wrap: wrap; margin-top: 20px;">
        <div class="aspects" style="flex: 1; min-width: 250px;">
          {#each Object.entries($result.detail_aspek) as [aspek, nilai]}
            <div class="aspect-row">
              <span>{aspek}</span>
              <strong>{Number(nilai).toFixed(2)}</strong>
            </div>
          {/each}
        </div>
        <div class="chart-wrapper" style="flex: 1; min-width: 280px; max-width: 400px; height: 300px;">
          <canvas use:renderRadarChart={$result}></canvas>
        </div>
      </div>
    </div>

    <!-- Mini Chat Interface -->
    <div class="mini-chat-section" style="margin-top: 30px; border-top: 1px solid var(--border-color); padding-top: 20px;">
      <h3 style="margin-bottom: 15px;">Diskusikan Hasil Ini</h3>
      
      <div class="messages" style="max-height: 300px; padding: 10px; background: #2a2a2a; border-radius: 12px; margin-bottom: 15px;">
        {#each $indexChat.messages as msg}
          <div class="message {msg.role}" style="padding: 10px;">
            <div class="avatar">{msg.role === 'assistant' ? '🤖' : '👤'}</div>
            <div class="bubble">{@html parseMarkdown(msg.content)}</div>
          </div>
        {/each}
        {#if $indexChat.isLoading}
          <div class="message assistant" style="padding: 10px;">
            <div class="avatar">🤖</div>
            <div class="bubble typing-indicator"><span></span><span></span><span></span></div>
          </div>
        {/if}
      </div>

      <div class="input-wrapper">
        <textarea 
          bind:value={chatInput} 
          on:keydown={handleChatKeydown}
          placeholder="Tanya AI tentang hasil evaluasi di atas..."
          rows="2"
        ></textarea>
        <button class="send-btn" on:click={handleChatSend} disabled={!chatInput.trim() || $indexChat.isLoading}>
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </div>
    </div>
  {/if}
</div>
