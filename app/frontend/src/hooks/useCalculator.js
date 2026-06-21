import { writable } from 'svelte/store';
import Swal from 'sweetalert2';

export function useCalculator() {
  const isLoading = writable(false);
  const result = writable(null);

  async function calculateIndex(indicators) {
    isLoading.set(true);
    try {
      const res = await fetch('/calculate-index', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ indicators })
      });
      
      if (!res.ok) throw new Error('API Error');

      const data = await res.json();
      result.set(data);
      
      Swal.fire({
        icon: 'success',
        title: 'Berhasil',
        text: 'Indeks berhasil dihitung!',
        timer: 1500,
        showConfirmButton: false,
        background: '#2f2f2f',
        color: '#fff'
      });
    } catch (e) {
      Swal.fire({
        icon: 'error',
        title: 'Gagal Menghitung',
        text: 'Pastikan server API berjalan.',
        background: '#2f2f2f',
        color: '#fff'
      });
    } finally {
      isLoading.set(false);
    }
  }

  function resetCalculator() {
    result.set(null);
  }

  return {
    isLoading,
    result,
    calculateIndex,
    resetCalculator
  };
}
