const CACHE_NAME = "social-app-cache-v1";
const urlsToCache = [
    "/",
    "/static/css/style.css",
    "/static/js/script.js",
    "/static/images/logo.png"
];

// تثبيت Service Worker وتخزين الملفات في الكاش
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(urlsToCache);
        })
    );
});

// جلب البيانات من الكاش عند عدم وجود إنترنت
self.addEventListener("fetch", (event) => {
    event.respondWith(
        fetch(event.request).catch(() => {
            return caches.match(event.request);
        })
    );
});
