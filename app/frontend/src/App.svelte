<script>
  import Sidebar from './components/Sidebar.svelte';
  import ChatInterface from './components/ChatInterface.svelte';
  import Calculator from './components/Calculator.svelte';

  let currentTab = 'chat'; // 'chat' or 'calculator'
</script>

<div class="app-container">
  <!-- Sidebar Component -->
  <Sidebar bind:currentTab={currentTab} />

  <!-- Main Content -->
  <main class="main-content">
    <ChatInterface isActive={currentTab === 'chat'} />
    <Calculator isActive={currentTab === 'calculator'} />
  </main>
</div>
