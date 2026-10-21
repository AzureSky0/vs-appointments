// Caches the app so it opens without internet. Bump VERSION when you change any file.
const VERSION = 'vs-appt-v5';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './apple-touch-icon.png', './icon-192.png', './icon-512.png'];
const NETWORK_TIMEOUT_MS = 4000;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== VERSION).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Network first (so updates show up), falling back to the saved copy when offline,
// when the network is very slow, or when the site returns an error page.
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(networkFirst(e.request));
});

async function networkFirst(request) {
  const fromCache = async () =>
    (await caches.match(request, { ignoreSearch: true })) ||
    (request.mode === 'navigate' ? caches.match('./index.html') : undefined);

  const network = fetch(request).then(res => {
    // Never cache or show an error page (404/500); use the saved copy instead.
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const copy = res.clone();
    caches.open(VERSION).then(c => c.put(request, copy));
    return res;
  });
  network.catch(() => {}); // handled below; avoids an "unhandled rejection" warning

  const slow = new Promise(resolve => setTimeout(() => resolve('slow'), NETWORK_TIMEOUT_MS));
  try {
    const first = await Promise.race([network, slow]);
    if (first !== 'slow') return first;
    // Weak signal: show the saved copy now if there is one, otherwise keep waiting.
    return (await fromCache()) || (await network);
  } catch {
    const cached = await fromCache();
    if (cached) return cached;
    return fetch(request); // nothing saved: let the browser show its normal error
  }
}
