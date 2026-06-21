<script>
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';

  let messages = [
    { role: 'assistant', content: 'Halo! Saya Agent Evaluasi Kinerja Pemdi. Ada yang bisa saya bantu terkait PermenPANRB No. 8 Tahun 2026?' }
  ];
  let inputMessage = '';
  let isLoading = false;
  let sessionId = 'session-' + Math.random().toString(36).substring(2, 9);

  export let isActive = true;

  async function sendMessage() {
    if (!inputMessage.trim()) return;
    
    const userMsg = inputMessage;
    messages = [...messages, { role: 'user', content: userMsg }];
    inputMessage = '';
    isLoading = true;

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, session_id: sessionId })
      });
      const data = await res.json();
      
      let botResponse = data.answer;
      if (data.sources && data.sources.length > 0) {
         botResponse += '\n\n**Sumber:**\n' + data.sources.map(s => `- Halaman ${s.page}`).join('\n');
      }

      messages = [...messages, { role: 'assistant', content: botResponse }];
    } catch (e) {
      messages = [...messages, { role: 'assistant', content: 'Maaf, terjadi kesalahan saat menghubungi server.' }];
    } finally {
      isLoading = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  function parseMarkdown(text) {
    if (!text) return '';
    return DOMPurify.sanitize(marked.parse(text));
  }
</script>

<style>
  :global(.bubble p) { margin-bottom: 0.5rem; }
  :global(.bubble p:last-child) { margin-bottom: 0; }
  :global(.bubble ul), :global(.bubble ol) { margin-left: 1.5rem; margin-bottom: 0.5rem; }
  :global(.bubble li) { margin-bottom: 0.25rem; }
  :global(.bubble strong) { font-weight: 600; color: #fff; }
</style>

<div class="chat-container" style="display: {isActive ? 'flex' : 'none'}">
  <div class="messages">
    {#each messages as msg}
      <div class="message {msg.role}">
        <div class="avatar">
          {msg.role === 'assistant' ? '🤖' : '👤'}
        </div>
        <div class="bubble">
          {@html parseMarkdown(msg.content)}
        </div>
      </div>
    {/each}
    {#if isLoading}
      <div class="message assistant">
        <div class="avatar">🤖</div>
        <div class="bubble typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    {/if}
  </div>
  <div class="input-area">
    <div class="input-wrapper">
      <textarea 
        bind:value={inputMessage} 
        on:keydown={handleKeydown}
        placeholder="Tanyakan sesuatu tentang Evaluasi Kinerja Pemdi..."
        rows="1"
      ></textarea>
      <button class="send-btn" on:click={sendMessage} disabled={!inputMessage.trim() || isLoading}>
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
      </button>
    </div>
  </div>
</div>
