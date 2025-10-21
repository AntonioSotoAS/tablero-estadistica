self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('app-cache-v1').then(cache => {
      return cache.addAll([
        '/', // La página principal
        '/static/base/css/styles.css', // Tu CSS
        '/static/js/main.js', // Tu JavaScript
        '/static/base/img/estadistica.ico' // Imágenes necesarias
      ]);
    })
  );
  console.log('Service Worker instalado.');
});

const CACHE_NAME = 'app-cache-v1';
const RESOURCES_TO_PRECACHE = [
    '/', // La página principal
    '/static/base/css/styles.css', // Tu CSS
    '/static/js/main.js', // Tu JavaScript
    '/static/base/img/estadistica.ico' // Imágenes necesarias
];

// Instalar y cachear recursos
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('Cache abierto');
      return cache.addAll(RESOURCES_TO_PRECACHE);
    })
  );
});

// Interceptar solicitudes
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      return cachedResponse || fetch(event.request);
    })
  );
});

// Actualizar caché
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (!cacheWhitelist.includes(cacheName)) {
            console.log(`Eliminando caché antiguo: ${cacheName}`);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
