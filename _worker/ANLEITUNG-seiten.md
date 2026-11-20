# Worker «seiten» — клиентские сайты «Website selbst» (20.11.2026)

Что это: клиентка сама меняет свой сайт (тексты, цены, часы, фото) по личной ссылке, правки сразу онлайн.
Оле приходит письмо со списком изменений, предыдущая версия хранится для отката.
Всё на бесплатном тарифе Cloudflare, **карта не нужна** (данные и фото — в KV, без R2).

Файлы: `_worker/seiten.js` (Worker), `website-selbst/index.html` (конструктор + режим правки), `website-selbst/vorschau.html` (шаблон = живой сайт).

**Порядок важен:** сначала шаги 1–5 (Worker работает), потом `git push` сайта (шаг 6). На странице конструктора уже написано «Sie ändern selbst».

---

## 1. Хранилище KV (≈ 2 мин)
Cloudflare (аккаунт olha.polishchuk.web) → **Storage & Databases → Workers KV → Create** → имя `seiten` → Create.

## 2. Worker (≈ 3 мин)
**Workers & Pages → Create → Worker** → имя **`seiten`** → Deploy → **Edit code** → удалить всё → вставить `_worker/seiten.js` → **Deploy**.

## 3. Привязать KV
Worker `seiten` → **Settings → Bindings → Add → KV namespace**: Variable name **`SITES`**, namespace `seiten` → Save → Deploy.

## 4. Переменные
Worker `seiten` → **Settings → Variables and Secrets → Add**:
| Имя | Тип | Значение |
|---|---|---|
| `ADMIN_TOKEN` | **Secret** | длинный случайный пароль (напр. 30+ символов из менеджера паролей). Это вход в /admin — никому не давать |
| `BREVO_API_KEY` | **Secret** | тот же ключ, что у Worker `kontakt` |
| `TO_EMAIL` | Text | `olha.polishchuk.web@gmail.com` |
| `FROM_EMAIL` | Text | `hello@olhapolishchuk.de` |

Адрес Worker должен быть `https://seiten.olha-polishchuk-web.workers.dev`.
Если другой — поменять `SITES_API` в начале скрипта `website-selbst/index.html` и ссылку в письме в `_worker/kontakt.js`.

## 5. Проверка (≈ 5 мин)
1. Открыть `https://seiten.olha-polishchuk-web.workers.dev/admin` → ввести `ADMIN_TOKEN` → «Войти».
2. «Новый сайт из заявки»: slug `test`, в поле JSON вставить вложение из любого тестового письма «[Website selbst] …» (или сам JSON заявки) → «Создать сайт».
3. Открыть ссылку проверки `…/s/test/` — сайт виден (без своих фото: без галереи и без портрета — так и задумано).
4. **Ссылку для правок** открыть **после шага 6** (конструктор должен быть уже на сайте): поменять слоган, загрузить фото, поставить галочку → «Änderungen veröffentlichen» → в Gmail письмо «[Website selbst] Änderung: …».
5. В /admin: «Откатить» → сайт вернулся к прежней версии. Потом «Удалить» тестовый сайт.

## 6. Опубликовать конструктор
```
cd E:\PROJECTS\MySite
git add -A
git commit -m "Website selbst: selbst bearbeiten (Worker seiten)"
git pull --no-edit
git push
```
И обновить Worker `kontakt` (`_worker/kontakt.js` → Edit code → вставить → Deploy): в письме с заявкой теперь подсказка про /admin.

---

## Запуск сайта клиентки (каждый раз)
1. Пришла заявка «[Website selbst] Studio – domain» → проверить тексты (HWG/UWG), Impressum, договор, счёт.
2. /admin → «Новый сайт из заявки»: slug (напр. `lumi-nails`), JSON из вложения → «Создать». Проверить `…/s/lumi-nails/`.
3. **Домен** на имя клиентки у INWX. В Cloudflare: **Add a domain** → Free → у INWX поменять nameserver на те, что покажет Cloudflare (вступает в силу до 24 ч).
4. Worker `seiten` → **Settings → Domains & Routes → Add → Custom domain**: `lumi-nails.de`, потом ещё раз `www.lumi-nails.de`. Cloudflare сам выпустит https.
5. /admin → у сайта «Домен» → `lumi-nails.de www.lumi-nails.de` (первый — главный, www перенаправляется).
6. Отправить клиентке **ссылку для правок** (WhatsApp/E-Mail) + короткую инструкцию: «Ссылку храните как пароль; фото загрузите сами; изменения сразу онлайн».
7. Через 1–2 дня: Search Console для домена клиентки (если это входит в пакет).

## Если что-то не так
- **Клиентка испортила сайт** → /admin → «Откатить» (одна версия назад). Письмо о каждой правке приходит в Gmail.
- **Ссылка потерялась / попала не туда** → /admin → «Новая ссылка» (старая сразу перестаёт работать).
- **Клиентка ушла** → /admin → «JSON» (сохранить себе) → «Удалить»; домен у клиентки остаётся.
- Правка видна не сразу в другом городе: KV обновляется по миру до ~1 минуты.

## Лимиты бесплатного тарифа (проверено 20.11.2026)
- KV: 100 000 чтений / день, 1 000 записей / день, 1 ГБ. Один просмотр сайта ≈ 2 чтения (фото кешируются). Одна публикация ≈ 2–3 записи, одно фото = 1 запись.
- Workers: 100 000 запросов / день, 10 мс CPU на запрос.
Хватит на десятки сайтов. Если когда-нибудь упрёмся — Workers Paid (5 $/мес) снимает лимиты.

## Юридическое — сделать до первой клиентки
- **AVV (Auftragsverarbeitungsvertrag)** с каждой клиенткой: ты хостишь её сайт через Cloudflare → ты её Auftragsverarbeiter (IP-адреса посетителей). Шаблон AVV — добавить к договору.
- **Datenschutz на сайтах клиенток** (текст в `vorschau.html`, функция `openLegal`): проверить формулировки, особенно фразу про EU-US Data Privacy Framework / Standardvertragsklauseln у Cloudflare, и сверить со своим `datenschutz.html`.
- **Договор** (`Uslugi/vorlagen/vertrag-webseite.md`): самостоятельные правки — ответственность клиентки за тексты и фото; твой сервис — техника, домен, юр. тексты, помощь в течение 2 рабочих дней; гарантия 19 €/мес на 12 месяцев для первых 5 студий; круг правок при запуске; что происходит при расторжении (JSON и домен — клиентке).
