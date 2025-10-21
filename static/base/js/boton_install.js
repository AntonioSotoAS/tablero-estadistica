let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
  // Evita que el navegador muestre su banner predeterminado
  e.preventDefault();
  deferredPrompt = e;

  // Muestra tu botón personalizado
  const installButton = document.getElementById('install-button');
  if (!installButton) {
    console.warn('El botón de instalación no está presente en el DOM.');
    return;
  }
  installButton.classList.remove('d-none'); // Muestra el botón

  // Maneja el clic en el botón
  installButton.addEventListener('click', () => {
    deferredPrompt.prompt();

    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        alert('¡Gracias por instalar nuestra PWA!');
      } else {
        alert('Esperamos que instales nuestra PWA más tarde.');
      }
      deferredPrompt = null;
    });
  })
});

// Oculta el botón si la app ya está instalada
window.addEventListener('appinstalled', () => {
  console.log('PWA instalada');
  const installButton = document.getElementById('install-button');
  installButton.classList.add('d-none'); // Oculta el botón
});

// Inicializa los tooltips de Bootstrap
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl);
});