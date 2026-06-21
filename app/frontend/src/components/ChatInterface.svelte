<script>
  import { marked } from 'marked';
  import DOMPurify from 'dompurify';
  import { useChat } from '../hooks/useChat.js';

  export let isActive = true;

  const chat = useChat();
  let inputMessage = '';

  function handleSend() {
    if (!inputMessage.trim()) return;
    chat.sendMessage(inputMessage);
    inputMessage = '';
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
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
    {#each $chat.messages as msg}
      <div class="message {msg.role}">
        <div class="avatar">
          {msg.role === 'assistant' ? '🤖' : '👤'}
        </div>
        <div class="bubble">
          {@html parseMarkdown(msg.content)}
        </div>
      </div>
    {/each}
    {#if $chat.isLoading}
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
      <button class="send-btn" on:click={handleSend} disabled={!inputMessage.trim() || $chat.isLoading}>
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
      </button>
    </div>
  </div>
</div>
