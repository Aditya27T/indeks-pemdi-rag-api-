import { writable } from 'svelte/store';
import Swal from 'sweetalert2';

export function useChat() {
  const { subscribe, set, update } = writable({
    messages: [
      { role: 'assistant', content: 'Halo! Saya Agent Evaluasi Kinerja Pemdi. Ada yang bisa saya bantu terkait PermenPANRB No. 8 Tahun 2026?' }
    ],
    isLoading: false,
    sessionId: 'session-' + Math.random().toString(36).substring(2, 9)
  });

  async function sendMessage(text) {
    if (!text.trim()) return;

    let currentSessionId;
    update(state => {
      currentSessionId = state.sessionId;
      return {
        ...state,
        messages: [...state.messages, { role: 'user', content: text }],
        isLoading: true
      };
    });

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, session_id: currentSessionId })
      });
      
      if (!res.ok) throw new Error('API Error');

      const data = await res.json();
      
      let botResponse = data.answer;
      if (data.sources && data.sources.length > 0) {
         botResponse += '\n\n**Sumber:**\n' + data.sources.map(s => `- Halaman ${s.page}`).join('\n');
      }

      update(state => ({
        ...state,
        messages: [...state.messages, { role: 'assistant', content: botResponse }],
        isLoading: false
      }));
    } catch (e) {
      update(state => ({ ...state, isLoading: false }));
      Swal.fire({
        icon: 'error',
        title: 'Koneksi Gagal',
        text: 'Maaf, terjadi kesalahan saat menghubungi server RAG.',
        background: '#2f2f2f',
        color: '#fff'
      });
    }
  }

  function clearChat() {
    set({
      messages: [
        { role: 'assistant', content: 'Halo! Saya Agent Evaluasi Kinerja Pemdi. Ada yang bisa saya bantu terkait PermenPANRB No. 8 Tahun 2026?' }
      ],
      isLoading: false,
      sessionId: 'session-' + Math.random().toString(36).substring(2, 9)
    });
  }

  return {
    subscribe,
    sendMessage,
    clearChat
  };
}
