# Форма, аналитика, картинки — что сделать Оле (08.11.2026)

Всё в коде уже готово. Осталось подключить сервисы. Порядок важен: **сначала Worker (шаги 1–2), потом push (шаг 4)**.
Если сделать push раньше, ничего не сломается: пока Worker не отвечает, посетитель увидит сообщение «не получилось — напишите в WhatsApp / E-Mail» со ссылками.

## 1. Brevo (≈ 10 мин)
1. Регистрация на https://www.brevo.com (бесплатный тариф: 300 писем в день). Лучше на olha.polishchuk.web@gmail.com.
2. **Senders, Domains & Dedicated IPs → Domains → Add a domain** → `olhapolishchuk.de`.
   Brevo покажет 2–3 DNS-записи (TXT `brevo-code`, DKIM, DMARC) → добавить их в Cloudflare (аккаунт olha.polishchuk.web → olhapolishchuk.de → DNS).
   Существующие MX-записи (Email Routing) **не трогать**.
3. **Senders → Add a sender**: имя `Website olhapolishchuk.de`, адрес `hello@olhapolishchuk.de` (подтверждение придёт в Gmail через Email Routing).
4. **SMTP & API → API Keys → Generate a new API key** → название `kontakt-worker` → скопировать ключ (он показывается один раз).

## 2. Cloudflare Worker (≈ 5 мин)
1. Cloudflare (аккаунт, где лежат демо `*.olha-polishchuk-web.workers.dev`) → **Workers & Pages → Create → Worker** → имя **`kontakt`** → Deploy.
2. **Edit code** → удалить всё → вставить содержимое `_worker/kontakt.js` → Deploy.
3. **Settings → Variables and Secrets → Add**:
   - `BREVO_API_KEY` — тип **Secret** — ключ из Brevo
   - `TO_EMAIL` — Text — `olha.polishchuk.web@gmail.com`
   - `FROM_EMAIL` — Text — `hello@olhapolishchuk.de`
4. Адрес Worker должен быть `https://kontakt.olha-polishchuk-web.workers.dev`.
   Если другой — поменять `FORM_ENDPOINT` в начале `_build/build_site.py` и пересобрать (шаг 4).

## 3. Umami (≈ 5 мин)
1. https://cloud.umami.is/signup → при регистрации выбрать **Data region: EU** (потом не поменять!). Тариф Hobby — бесплатный.
2. **Settings → Websites → Add website**: Name `olhapolishchuk.de`, Domain `olhapolishchuk.de`.
3. **Edit → Tracking code**: скопировать `data-website-id="…"` (и адрес `src`, если он не `https://cloud.umami.is/script.js`).
4. В `_build/build_site.py` вписать: `UMAMI_ID = "…"` (и `UMAMI_SRC`, если отличается).
5. Чтобы не считать свои визиты: в браузере на сайте открыть консоль (F12) и выполнить `localStorage.setItem('umami.disabled', 1)`.

## 4. Собрать и опубликовать
```
cd E:\PROJECTS\MySite
python _build/build_site.py
python _build/build_blog.py
python _build/build_checklist.py
python _build/build_landing.py
git add -A
git commit -m "Formular per Worker+Brevo, AVIF/WebP, Umami, Skip-Link"
git push
```
Новые картинки потом: добавить в список `IMAGES` в `_build/optimize_images.py` → `pip install --upgrade pillow` (один раз) → `python _build/optimize_images.py` → сборка.

## 5. Проверка после публикации
- Отправить себе тестовую заявку с телефона (подождать 3+ секунды перед отправкой — быстрее бот-фильтр молча отбрасывает) → письмо в Gmail, «Ответить» идёт сразу на адрес из формы.
- PageSpeed Insights: https://pagespeed.web.dev/?url=https://olhapolishchuk.de
- Umami → Realtime: виден свой визит (если не отключили в п. 3.5).

## События в Umami (Events)
| Событие | Что это |
|---|---|
| `hero-cta` | кнопка «Kostenloser Google-Check» в шапке |
| `paket-anfragen` (+ `paket`: A/B/C) | «Anfragen» под пакетом |
| `kontakt-whatsapp` / `kontakt-email` / `kontakt-linkedin` | иконки в блоке контактов |
| `whatsapp-float` | круглая зелёная кнопка WhatsApp в углу (видна всегда) |
| `formular-gesendet` / `formular-fehler` | форма ушла / не ушла |
| `puzzle-geloest`, `puzzle-checkliste`, `puzzle-whatsapp` | пазл в «Обо мне» |
