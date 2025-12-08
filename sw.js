// sw.js (Service Worker)
const CACHE_NAME = 'asesor-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/manifest.json',
    // Opcional: añade el favicon.png si lo subes
];

// 1. Instalar Service Worker y Cachear archivos estáticos
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// 2. Interceptar peticiones para servir desde el cache
self.addEventListener('fetch', event => {
  event.respondswith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
