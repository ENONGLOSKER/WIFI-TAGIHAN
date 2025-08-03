// Format mata uang IDR untuk semua elemen dengan class 'currency'
  document.querySelectorAll('.currency').forEach(function(el) {
    let value = el.textContent.replace(/[^\d]/g, '');
    if (value) {
      el.textContent = new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        maximumFractionDigits: 0
      }).format(value);
    }
  });