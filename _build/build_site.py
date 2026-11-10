#!/usr/bin/env python3
"""Собирает три языковые версии главной olhapolishchuk.de: / (DE), /uk/ (UA), /ru/ (RU).

Запуск из корня репозитория:  python _build/build_site.py
Тексты правятся в словаре T ниже, дизайн — в CSS. Папка _build на сайт не публикуется (Jekyll).
"""
import html
import json
import os
import sys

SITE = "https://olhapolishchuk.de/"
EMAIL = "olha.polishchuk.web@gmail.com"
WA_NUM = "380666578075"
LINKEDIN = "https://linkedin.com/in/olha-882b30113"
PATHS = {"de": "", "uk": "uk/", "ru": "ru/"}
LABELS = {"de": "DE", "uk": "UA", "ru": "RU"}
LOCALE = {"de": "de_DE", "uk": "uk_UA", "ru": "ru_RU"}
# Ссылка на Google-профиль (Google Maps → «Поделиться» → скопировать ссылку). Пусто — не выводится.
GBP_URL = "https://share.google/Fj5iyprSwlv8rUxlQ"

# ── Форма: адрес Cloudflare Worker, который пересылает заявку письмом (через Brevo).
#    Код воркера: _worker/kontakt.js. Если воркер недоступен — форма откроет почтовую программу, как раньше.
FORM_ENDPOINT = "https://kontakt.olha-polishchuk-web.workers.dev"

# ── Аналитика Umami Cloud (без cookies, баннер не нужен). Пустой ID → скрипт не вставляется.
#    ID и адрес скрипта: Umami → Settings → Websites → Edit → Tracking code.
UMAMI_SRC = "https://cloud.umami.is/script.js"
UMAMI_ID = "fe1a89e7-ba92-4d19-99cf-5949bb100cdd"


def analytics_html():
    if not UMAMI_ID:
        return ""
    return ('<script defer src="%s" data-website-id="%s" data-domains="olhapolishchuk.de" '
            'data-do-not-track="true"></script>\n' % (UMAMI_SRC, UMAMI_ID))


# ── Картинки: <picture> с AVIF/WebP (файлы готовит _build/optimize_images.py)
_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
_BLANK = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"


def pic(src, w, h, alt, widths, sizes, attrs='loading="lazy" decoding="async"', hide_below=None):
    """src — путь от корня сайта (/images/x.jpg). Если готовых AVIF/WebP нет — обычный <img>.
    hide_below=900 — на экранах уже 900 px картинка скрыта CSS-ом, браузер её не скачивает."""
    base = os.path.splitext(src)[0]
    have = [x for x in widths if os.path.exists(os.path.join(_ROOT, "%s-%d.avif" % (base.lstrip("/"), x)))]
    img = '<img src="%s" width="%d" height="%d" alt="%s" %s>' % (src, w, h, html.escape(alt, quote=True), attrs)
    if not have:
        return img
    o = ["<picture>"]
    if hide_below:
        o.append('<source media="(max-width:%dpx)" srcset="%s">' % (hide_below, _BLANK))
    for ext in ("avif", "webp"):
        srcset = ", ".join("%s-%d.%s %dw" % (base, x, ext, x) for x in have)
        o.append('<source type="image/%s" srcset="%s" sizes="%s">' % (ext, srcset, sizes))
    o.append(img + "</picture>")
    return "".join(o)


FORM_UI = {
    "de": dict(sending="Wird gesendet …", ok_t="Danke, Ihre Anfrage ist angekommen!",
               ok="Ich melde mich in Kürze per E-Mail.",
               err="Das hat leider nicht geklappt. Bitte schreiben Sie mir direkt:"),
    "uk": dict(sending="Надсилаю…", ok_t="Дякую, заявку отримано!",
               ok="Я напишу вам на e-mail найближчим часом.",
               err="На жаль, не вдалося надіслати. Напишіть мені напряму:"),
    "ru": dict(sending="Отправляю…", ok_t="Спасибо, заявка получена!",
               ok="Я напишу вам на e-mail в ближайшее время.",
               err="К сожалению, отправить не получилось. Напишите мне напрямую:"),
}

# ── Календарь записи (блок «Kontakt»). Открытые дни берутся из файла /termine.csv в корне сайта
#    (правится прямо на GitHub: дата, время, заметка). Если файла нет или в нём нет будущих дат —
#    запасной вариант: недельная сетка CAL_SLOTS (0 = вс, 1 = пн … 6 = сб), праздники NRW закрыты.
#    Выбранное время уходит вместе с формой (поле termin) — подтверждать клиенту вручную по e-mail.
CAL_SLOTS = {1: "12:00", 3: "18:00", 4: "10:00"}
CAL_UI = {
    "de": dict(loc="de-DE", wd=["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"],
               title="Oder direkt einen Termin wählen",
               sub="Kostenloses Erstgespräch, ca. 20 Min., per Telefon oder Video.",
               free="frei", none="keine Termine", prev="Vorheriger Monat", next="Nächster Monat",
               chip="Wunschtermin:", remove="Termin entfernen", btn="Termin anfragen →",
               note="Ich bestätige den Termin per E-Mail."),
    "uk": dict(loc="uk-UA", wd=["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
               title="Або одразу оберіть час зустрічі",
               sub="Безкоштовна перша розмова, ~20 хв, телефоном або по відео.",
               free="вільно", none="немає прийому", prev="Попередній місяць", next="Наступний місяць",
               chip="Бажаний час:", remove="Скасувати вибір", btn="Записатися →",
               note="Я підтверджу зустріч на e-mail."),
    "ru": dict(loc="ru-RU", wd=["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
               title="Или сразу выберите время встречи",
               sub="Бесплатный первый разговор, ~20 мин, по телефону или видео.",
               free="свободно", none="нет приёма", prev="Предыдущий месяц", next="Следующий месяц",
               chip="Желаемое время:", remove="Отменить выбор", btn="Записаться →",
               note="Я подтвержу встречу по e-mail."),
}

SKIP_LABEL = {"de": "Zum Inhalt springen", "uk": "Перейти до змісту", "ru": "Перейти к содержанию"}

CYR = "U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"
LAT = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,"
       "U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD")


def face(fam, style, weight, file, rng):
    return ("@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;"
            "src:url(/fonts/%s) format('woff2');unicode-range:%s}\n" % (fam, style, weight, file, rng))


FONTS = "".join([
    face("DM Sans", "normal", "300", "dm-sans-latin-300-normal.woff2", LAT),
    face("DM Sans", "normal", "400", "dm-sans-latin-400-normal.woff2", LAT),
    face("DM Sans", "italic", "400", "dm-sans-latin-400-italic.woff2", LAT),
    face("DM Sans", "normal", "500", "dm-sans-latin-500-normal.woff2", LAT),
    face("DM Sans", "normal", "600 700", "dm-sans-latin-600-normal.woff2", LAT),
    face("DM Serif Display", "normal", "400", "dm-serif-display-latin-400-normal.woff2", LAT),
    face("DM Serif Display", "italic", "400", "dm-serif-display-latin-400-italic.woff2", LAT),
    # Кириллица: Onest (к DM Sans) и Playfair Display (к DM Serif Display), тоже локально
    face("DM Sans", "normal", "300", "onest-cyrillic-300-normal.woff2", CYR),
    face("DM Sans", "normal", "400", "onest-cyrillic-400-normal.woff2", CYR),
    face("DM Sans", "italic", "400", "onest-cyrillic-400-normal.woff2", CYR),
    face("DM Sans", "normal", "500", "onest-cyrillic-500-normal.woff2", CYR),
    face("DM Sans", "normal", "600 700", "onest-cyrillic-600-normal.woff2", CYR),
    face("DM Serif Display", "normal", "400", "playfair-display-cyrillic-600-normal.woff2", CYR),
    face("DM Serif Display", "italic", "400", "playfair-display-cyrillic-600-italic.woff2", CYR),
])

CSS = r"""
:root{--ink:#1E2A4A;--ink-soft:#4A5568;--amber:#D48B3A;--amber-light:#E8A84F;--amber-pale:#FDF3E7;--bg:#FFFFFF;--bg-soft:#F7F6F4;--bg-mid:#EEF0F5;--line:rgba(30,42,74,0.1);--r:6px}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:'DM Sans',sans-serif;color:var(--ink);background:var(--bg);-webkit-font-smoothing:antialiased;line-height:1.65}
a{color:inherit;text-decoration:none}
img{display:block;max-width:100%}
.wrap{max-width:1100px;margin:0 auto;padding:0 28px}
section[id]{scroll-margin-top:72px}

/* SKIP-LINK (Tastatur/Screenreader) */
.skip{position:absolute;left:12px;top:-60px;z-index:200;background:var(--ink);color:#fff;padding:10px 16px;border-radius:8px;font-size:14px;font-weight:600}
.skip:focus{top:10px}
main:focus{outline:none}
/* NAV */
header{position:sticky;top:0;z-index:100;background:rgba(255,255,255,0.94);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
nav.wrap{display:flex;align-items:center;justify-content:space-between;height:64px;gap:16px}
.brand{display:flex;align-items:center;gap:10px}
.brand-init{width:36px;height:36px;border-radius:50%;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:600;letter-spacing:0.02em;flex-shrink:0}
.brand-name{font-size:15px;font-weight:600;letter-spacing:-0.01em}
.brand-name span{color:var(--amber)}
.nav-links{display:flex;gap:24px}
.nav-links a{font-size:13.5px;font-weight:500;color:var(--ink-soft);transition:color .2s}
.nav-links a:hover{color:var(--ink)}
.nav-right{display:flex;align-items:center;gap:14px}
.lang-sw{display:flex;border:1px solid var(--line);border-radius:20px;overflow:hidden}
.lang-sw a{font-size:12px;font-weight:600;letter-spacing:0.06em;color:var(--ink-soft);padding:5px 12px;transition:all .2s}
.lang-sw a:hover{color:var(--ink);background:var(--bg-soft)}
.lang-sw a.on{background:var(--ink);color:#fff}
.cta-nav{font-size:13px;font-weight:600;padding:9px 18px;background:var(--amber);color:#fff;border-radius:var(--r);transition:all .2s;white-space:nowrap}
.cta-nav:hover{background:var(--amber-light);transform:translateY(-1px)}

/* HERO */
.hero{padding:88px 0 64px;background:var(--bg)}
.hero-inner{display:grid;grid-template-columns:1fr 420px;gap:60px;align-items:center}
.hero-eyebrow{display:inline-flex;align-items:center;gap:8px;background:var(--amber-pale);color:#9A6424;font-size:12px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;padding:6px 14px;border-radius:20px;margin-bottom:22px}
.hero-eyebrow::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--amber);flex-shrink:0}
.hero h1{font-size:1.02rem;font-weight:600;line-height:1.45;letter-spacing:0;margin-bottom:12px;color:var(--ink);max-width:46ch}
.hero-claim{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(2.3rem,4.4vw,3.5rem);line-height:1.1;letter-spacing:-0.02em;margin-bottom:20px;color:var(--ink)}
.hero-claim em{font-style:italic;color:var(--amber)}
.hero-sub{font-size:1.08rem;font-weight:300;color:var(--ink-soft);max-width:50ch;line-height:1.75;margin-bottom:34px}
.hero-btns{display:flex;gap:14px;flex-wrap:wrap}
.btn-primary{display:inline-flex;align-items:center;gap:8px;padding:13px 26px;background:var(--ink);color:#fff;border-radius:var(--r);font-size:14px;font-weight:600;transition:all .25s}
.btn-primary:hover{background:#2d3f6b;transform:translateY(-2px)}
.btn-outline{display:inline-flex;align-items:center;gap:8px;padding:12px 24px;border:1.5px solid var(--line);color:var(--ink);border-radius:var(--r);font-size:14px;font-weight:500;transition:all .25s}
.btn-outline:hover{border-color:var(--ink);background:var(--bg-soft)}
.hero-photo{position:relative}
.hero-photo-frame{aspect-ratio:4/5;border-radius:16px;overflow:hidden;background:var(--bg-mid)}
.hero-photo-frame img{width:100%;height:100%;object-fit:cover}
.hero-badge{position:absolute;bottom:-18px;right:-18px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px 18px;box-shadow:0 4px 24px rgba(30,42,74,0.08);max-width:190px}
.hero-badge-num{font-family:'DM Serif Display',serif;font-size:1.9rem;color:var(--ink);line-height:1}
.hero-badge-lbl{font-size:12px;color:var(--ink-soft);margin-top:4px;line-height:1.4}

/* METRICS */
.metrics{background:var(--ink);padding:28px 0}
.metrics-inner{display:flex;justify-content:space-around;gap:20px;flex-wrap:wrap}
.metric{text-align:center}
.metric-num{font-family:'DM Serif Display',serif;font-size:1.9rem;color:#fff;line-height:1.1}
.metric-lbl{font-size:12.5px;color:rgba(255,255,255,0.72);margin-top:4px;letter-spacing:0.03em}

/* COMMON */
.sec-label{font-size:11.5px;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#9A6424;margin-bottom:12px}
.sec-title{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(1.8rem,3vw,2.5rem);line-height:1.15;letter-spacing:-0.01em;margin-bottom:40px;max-width:30ch}

/* WHY */
.why{padding:88px 0}
.why-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.svc{background:#fff;border:1px solid var(--line);border-radius:12px;padding:28px 24px;transition:all .3s;position:relative;overflow:hidden}
.svc::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;background:var(--amber);transform:scaleX(0);transform-origin:left;transition:transform .3s}
.svc:hover::before{transform:scaleX(1)}
.svc:hover{border-color:rgba(212,139,58,0.3);transform:translateY(-4px);box-shadow:0 12px 40px rgba(30,42,74,0.08)}
.svc-icon{width:44px;height:44px;border-radius:10px;background:var(--amber-pale);display:flex;align-items:center;justify-content:center;margin-bottom:18px}
.svc-icon svg{width:22px;height:22px;color:var(--amber)}
.svc h3{font-size:16px;font-weight:600;margin-bottom:8px;line-height:1.35}
.svc p{font-size:14px;color:var(--ink-soft);line-height:1.65}

/* PACKAGES */
.pakete{padding:88px 0;background:var(--bg-soft)}
.pkg-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;align-items:stretch}
.pkg{background:#fff;border:1px solid var(--line);border-radius:14px;padding:30px 26px;display:flex;flex-direction:column}
.pkg.feat{border-color:rgba(212,139,58,0.55);box-shadow:0 12px 40px rgba(212,139,58,0.12)}
.pkg-tag{font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#9A6424;margin-bottom:10px}
.pkg h3{font-size:18px;font-weight:600;line-height:1.35}
.pkg-price{font-family:'DM Serif Display',serif;font-size:2.6rem;line-height:1.1;margin:12px 0 12px}
.pkg-price s.old{font-size:.62em;color:var(--ink-soft);text-decoration:line-through;text-decoration-color:#D62828;text-decoration-thickness:3px;margin-right:6px;vertical-align:middle}
.pkg-price small{font-family:'DM Sans',sans-serif;font-size:15px;color:var(--ink-soft);font-weight:500}
.pkg-start{background:var(--amber-pale);color:#7A4E17;font-size:13.5px;line-height:1.5;padding:10px 12px;border-radius:8px;margin-bottom:16px}
.pkg-desc{font-size:14.5px;color:var(--ink-soft);margin-bottom:14px}
.pkg ul{list-style:none;display:flex;flex-direction:column;gap:8px;margin-bottom:18px}
.pkg li{font-size:14px;line-height:1.55;padding-left:24px;position:relative}
.pkg li::before{content:"";position:absolute;left:2px;top:6px;width:11px;height:6px;border-left:2px solid var(--amber);border-bottom:2px solid var(--amber);transform:rotate(-45deg)}
.pkg-term{font-size:13px;color:var(--ink-soft);margin-top:auto;padding-top:14px;border-top:1px solid var(--line)}
.pkg-btn{margin-top:16px;display:flex;justify-content:center;padding:12px 18px;border-radius:var(--r);background:var(--ink);color:#fff;font-weight:600;font-size:14px;transition:background .2s}
.pkg-btn:hover{background:#2d3f6b}
.pkg-extras{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:18px}
.pkg-extra{background:#fff;border:1px dashed rgba(30,42,74,0.28);border-radius:14px;padding:20px 22px;font-size:14.5px;color:var(--ink-soft);line-height:1.6}
.pkg-extra strong{color:var(--ink)}
a.inl{color:#9A6424;font-weight:600;text-decoration:underline;text-underline-offset:3px}
a.inl:hover{color:var(--ink)}
.pkg-note{font-size:13px;color:var(--ink-soft);margin-top:22px;max-width:85ch}

/* STEPS */
.ablauf{padding:88px 0}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:28px}
.step{position:relative;padding-top:58px}
.step-num{position:absolute;top:0;left:0;width:42px;height:42px;border-radius:50%;background:var(--ink);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:15px}
.step::after{content:"";position:absolute;top:21px;left:54px;right:-16px;height:1px;background:rgba(30,42,74,0.18)}
.step:last-child::after{display:none}
.step h3{font-size:16px;font-weight:600;margin-bottom:8px}
.step p{font-size:14px;color:var(--ink-soft);line-height:1.65}

/* CASES */
.cases{padding:88px 0;background:var(--bg-soft)}
.cases-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.demo-head{margin:48px 0 18px}
.demo-head h3{font-family:'DM Serif Display',serif;font-weight:400;font-size:1.6rem;line-height:1.2}
.demo-head p{color:var(--ink-soft);font-size:14.5px;margin-top:6px}
.case{background:#fff;border:1px solid var(--line);border-radius:12px;padding:28px;transition:all .3s}
.case:hover{transform:translateY(-3px);box-shadow:0 10px 36px rgba(30,42,74,0.07)}
.case.wide{grid-column:1/-1}
.case.wide p{max-width:80ch}
.case-tag{font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#9A6424;margin-bottom:10px}
.case h3{font-size:17px;font-weight:600;margin-bottom:10px;line-height:1.4}
.case h3 a{border-bottom:1px solid rgba(212,139,58,0.5)}
.case h3 a:hover{color:var(--amber)}
.case p{font-size:14px;color:var(--ink-soft);line-height:1.7;margin-bottom:18px}
.case-result{display:flex;gap:28px;flex-wrap:wrap}
.result-item .r-num{font-family:'DM Serif Display',serif;font-size:1.6rem;color:var(--ink);line-height:1.2}
.result-item .r-lbl{font-size:12px;color:var(--ink-soft);margin-top:2px;max-width:22ch;line-height:1.4}
.case.has-img{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:32px;align-items:center}
.case-img{display:block;border-radius:8px;overflow:hidden;border:1px solid var(--line);line-height:0}
.case-img img{width:100%;height:auto;display:block}
.case.has-img .case-result{gap:22px}
.case.has-img .r-lbl{max-width:17ch}
.case-quote{border-left:3px solid var(--amber);padding:2px 0 2px 16px;margin:0 0 18px;font-style:italic;font-size:14.5px;color:var(--ink);line-height:1.65}
.case-quote cite{display:block;font-style:normal;font-size:12px;color:var(--ink-soft);margin-top:6px}
.also{margin-top:20px;font-size:15px;color:var(--ink-soft);background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 22px}
.also strong{color:var(--ink)}

/* ABOUT */
.about{padding:88px 0}
.about-grid{display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center}
.about-img{position:relative}
.about-img-frame{aspect-ratio:1/1;border-radius:16px;overflow:hidden;background:var(--bg-mid)}
.about-img-frame img{width:100%;height:100%;object-fit:cover}
.about-card{position:absolute;bottom:-20px;left:-20px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 20px;min-width:200px}
.about-card-title{font-size:12px;color:var(--ink-soft);margin-bottom:8px;letter-spacing:0.04em}
.about-card-langs{display:flex;flex-direction:column;gap:5px}
.lang-row{display:flex;align-items:center;gap:8px;font-size:13px}
.lang-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0}
.about-text h2{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(1.8rem,3vw,2.5rem);line-height:1.12;margin-bottom:18px}
.about-text p{font-size:1rem;color:var(--ink-soft);margin-bottom:14px;line-height:1.75}
.about-skills{display:flex;flex-wrap:wrap;gap:8px;margin-top:24px}
.skill{font-size:12.5px;font-weight:500;padding:7px 14px;border:1px solid var(--line);border-radius:20px;color:var(--ink-soft)}

/* FAQ */
.faq{padding:88px 0;background:var(--bg-soft)}
.faq-list{display:flex;flex-direction:column;gap:10px;max-width:820px}
.faq details{background:#fff;border:1px solid var(--line);border-radius:12px;padding:0 22px}
.faq summary{cursor:pointer;list-style:none;font-weight:600;font-size:16px;padding:18px 32px 18px 0;position:relative}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";position:absolute;right:0;top:12px;font-size:24px;font-weight:400;color:var(--amber)}
.faq details[open] summary::after{content:"\2013"}
.faq details p{font-size:15px;color:var(--ink-soft);padding-bottom:18px;line-height:1.7}

/* CONTACT */
.contact{padding:88px 0;background:var(--ink)}
.contact-inner{display:grid;grid-template-columns:1.1fr 0.9fr;gap:60px;align-items:start}
.contact h2{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(1.9rem,3.5vw,2.8rem);line-height:1.1;color:#fff;margin-bottom:16px}
.contact h2 em{font-style:italic;color:var(--amber-light)}
.contact-sub{font-size:1rem;color:rgba(255,255,255,0.75);margin-bottom:32px;font-weight:300;max-width:46ch;line-height:1.75}
.contact-methods{display:flex;flex-direction:row;flex-wrap:wrap;gap:16px}
.cm{display:flex;align-items:center;justify-content:center;padding:10px;border-radius:50%;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);transition:all .25s;color:#fff}
.cm:hover{background:rgba(255,255,255,0.1);border-color:var(--amber);transform:translateY(-3px)}
.wa-float{position:fixed;right:18px;bottom:18px;z-index:150;width:58px;height:58px;border-radius:50%;background:#25D366;color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 6px 20px rgba(0,0,0,0.22);transition:transform .2s,box-shadow .2s}
.wa-float svg{width:30px;height:30px}
.wa-float:hover{transform:scale(1.07);box-shadow:0 8px 26px rgba(0,0,0,0.28)}
.wa-float:focus-visible{outline:3px solid var(--amber);outline-offset:3px}
@media(max-width:560px){.wa-float{right:14px;bottom:14px;width:54px;height:54px}}
@media print{.wa-float{display:none}}
.cm.wa{background:rgba(37,211,102,0.12);border-color:rgba(37,211,102,0.4)}
.cm-ic{width:44px;height:44px;border-radius:50%;background:rgba(212,139,58,0.2);display:flex;align-items:center;justify-content:center;flex-shrink:0}
.cm.wa .cm-ic{background:rgba(37,211,102,0.22)}
.cm-ic svg{width:22px;height:22px;color:var(--amber-light)}
.cm.wa .cm-ic svg{color:#4BE08A}
.cm-info .cm-label{font-size:11px;color:rgba(255,255,255,0.6);letter-spacing:0.06em;text-transform:uppercase}
.cm-info .cm-val{font-size:14px;font-weight:500;color:#fff;margin-top:2px}
.contact-form{background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:28px}
.contact-form h3{font-size:15px;font-weight:600;color:#fff;margin-bottom:20px}
.form-row{margin-bottom:14px}
.form-row label{display:block;font-size:12px;color:rgba(255,255,255,0.65);letter-spacing:0.05em;text-transform:uppercase;margin-bottom:6px}
.form-row input,.form-row textarea{width:100%;background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.14);border-radius:var(--r);color:#fff;font-family:'DM Sans',sans-serif;font-size:14px;padding:11px 14px;outline:none;transition:border .2s;resize:none}
.form-row input::placeholder,.form-row textarea::placeholder{color:rgba(255,255,255,0.4)}
.form-row input:focus,.form-row textarea:focus{border-color:var(--amber)}
.form-row textarea{height:90px}
.form-submit{width:100%;padding:13px;background:var(--amber);color:#fff;border:none;border-radius:var(--r);font-family:'DM Sans',sans-serif;font-size:14px;font-weight:600;cursor:pointer;transition:all .25s;margin-top:4px}
.form-submit:hover{background:var(--amber-light)}
.form-submit:disabled{opacity:.7;cursor:wait}
.hp{position:absolute!important;left:-9999px;width:1px;height:1px;overflow:hidden}
/* KALENDER */
.cal{margin-top:36px;background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:22px;color:#fff;max-width:440px}
.cal h3{font-size:15px;font-weight:600;margin-bottom:4px}
.cal-sub{font-size:13px;color:rgba(255,255,255,0.65);margin-bottom:16px;line-height:1.5}
.cal-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.cal-month{font-weight:600;font-size:14.5px;text-transform:capitalize}
.cal-nav{width:34px;height:34px;border-radius:50%;border:1px solid rgba(255,255,255,0.2);background:transparent;color:#fff;cursor:pointer;font-size:15px;line-height:1;font-family:inherit}
.cal-nav:hover:not(:disabled){border-color:var(--amber)}
.cal-nav:disabled{opacity:.25;cursor:default}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:4px}
.cal-wd{font-size:11px;text-align:center;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:.04em;padding-bottom:4px}
.cal-d{aspect-ratio:1;border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:13px;color:rgba(255,255,255,0.25);border:1px solid transparent;background:transparent;font-family:inherit;padding:0}
.cal-d.free{background:rgba(212,139,58,0.16);border-color:rgba(212,139,58,0.5);color:#fff;font-weight:600;cursor:pointer;transition:background .2s}
.cal-d.free small{font-size:10px;font-weight:500;color:var(--amber-light);line-height:1;margin-top:3px}
.cal-d.free:hover{background:rgba(212,139,58,0.32)}
.cal-d.free:focus-visible{outline:2px solid var(--amber-light);outline-offset:2px}
.cal-d.sel{background:var(--amber);border-color:var(--amber)}
.cal-d.sel small{color:#fff}
.cal-d.today{border-color:rgba(255,255,255,0.25)}
.cal-times{display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-top:12px;font-size:13px;color:rgba(255,255,255,0.75)}
.cal-times[hidden]{display:none}
.cal-t{border:1px solid rgba(212,139,58,0.6);background:rgba(212,139,58,0.16);color:#fff;border-radius:20px;padding:6px 14px;font-size:13px;font-weight:600;cursor:pointer;font-family:inherit}
.cal-t:hover,.cal-t.sel{background:var(--amber);border-color:var(--amber)}
.cal-legend{display:flex;gap:18px;font-size:12px;color:rgba(255,255,255,0.6);margin-top:12px}
.cal-legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.cal-legend .lf{background:rgba(212,139,58,0.5)}
.cal-legend .ln{background:rgba(255,255,255,0.12)}
.form-termin{display:flex;align-items:center;justify-content:space-between;gap:10px;background:rgba(212,139,58,0.16);border:1px solid rgba(212,139,58,0.5);border-radius:var(--r);padding:10px 12px 10px 14px;font-size:13.5px;color:#fff;margin-bottom:14px;line-height:1.45}
.form-termin[hidden]{display:none}
.form-termin b{font-weight:600}
.form-termin em{display:block;font-style:normal;font-size:12px;color:rgba(255,255,255,0.65)}
.form-termin button{background:none;border:0;color:rgba(255,255,255,0.75);cursor:pointer;font-size:20px;line-height:1;padding:2px 6px;font-family:inherit}
.form-termin button:hover{color:#fff}
@media(max-width:900px){.cal{max-width:none}}
.form-status{font-size:13.5px;line-height:1.5;margin-top:12px;min-height:1px}
.form-status.err{color:#FFC9A8}
.form-status a{color:#fff;text-decoration:underline;text-underline-offset:3px;font-weight:600}
.form-ok{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.14);border-radius:12px;padding:36px 28px;text-align:center;color:#fff}
.form-ok:focus{outline:none}
.form-ok-ic{width:52px;height:52px;margin:0 auto 16px;border-radius:50%;background:var(--amber);display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:700}
.form-ok h3{font-size:18px;font-weight:600;margin-bottom:8px}
.form-ok p{font-size:14.5px;color:rgba(255,255,255,0.75)}
.form-note{font-size:12px;color:rgba(255,255,255,0.55);margin-top:12px;line-height:1.5}
.form-note a{color:rgba(255,255,255,0.8);text-decoration:underline}

/* FOOTER */
footer{background:#111827;padding:32px 0}
.foot-inner{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}
.foot-copy{font-size:13px;color:rgba(255,255,255,0.5)}
.foot-links{display:flex;gap:20px;flex-wrap:wrap}
.foot-links a{font-size:13px;color:rgba(255,255,255,0.5);transition:color .2s}
.foot-links a:hover{color:rgba(255,255,255,0.85)}

/* BURGER / MOBILE MENU */
.burger{display:none;width:42px;height:42px;border:1px solid var(--line);border-radius:10px;background:#fff;cursor:pointer;align-items:center;justify-content:center;flex-shrink:0}
.burger span,.burger span::before,.burger span::after{display:block;width:18px;height:2px;background:var(--ink);border-radius:2px;position:relative;transition:transform .25s,background .25s}
.burger span::before,.burger span::after{content:"";position:absolute;left:0}
.burger span::before{top:-6px}.burger span::after{top:6px}
header.open .burger span{background:transparent}
header.open .burger span::before{transform:translateY(6px) rotate(45deg)}
header.open .burger span::after{transform:translateY(-6px) rotate(-45deg)}
.mnav{display:none;border-top:1px solid var(--line);background:#fff;max-height:calc(100vh - 64px);overflow-y:auto}
.mnav .wrap{display:flex;flex-direction:column;padding-top:8px;padding-bottom:20px}
.mnav a.ml{font-size:16px;font-weight:500;color:var(--ink);padding:14px 2px;border-bottom:1px solid var(--line)}
.mnav a.ml:active{color:var(--amber)}
.mnav .cta-m{margin-top:18px;text-align:center;font-size:15px;font-weight:600;padding:14px 18px;background:var(--amber);color:#fff;border-radius:var(--r)}
header.open .mnav{display:block}
.nav-links a.cur{color:var(--ink)}
@media(max-width:980px){.burger{display:inline-flex}}
@media(min-width:981px){.mnav{display:none!important}}
@media(max-width:400px){.brand-name{display:none}}

/* BLOG */
.blog-hero{padding:64px 0 32px}
.blog-hero h1{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(2rem,4vw,3rem);line-height:1.12;margin-bottom:14px}
.blog-hero p{color:var(--ink-soft);font-size:1.05rem;max-width:60ch}
.post-list{display:grid;gap:18px;padding-bottom:88px}
.post-card{display:block;background:#fff;border:1px solid var(--line);border-radius:14px;padding:28px 26px;transition:all .25s}
.post-card:hover{border-color:rgba(212,139,58,0.4);transform:translateY(-3px);box-shadow:0 12px 40px rgba(30,42,74,0.08)}
.post-meta{font-size:12.5px;color:#9A6424;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:8px}
.post-card h2{font-size:1.3rem;font-weight:600;line-height:1.35;margin-bottom:8px}
.post-card p{color:var(--ink-soft);font-size:15px}
.post-more{display:inline-block;margin-top:12px;color:var(--amber);font-weight:600;font-size:14px}
article.post{max-width:740px;margin:0 auto;padding:56px 28px 88px}
.crumbs{font-size:13px;color:var(--ink-soft);margin-bottom:22px}
.crumbs a{color:var(--amber)}
article.post h1{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(2rem,4.2vw,2.8rem);line-height:1.13;letter-spacing:-0.01em;margin-bottom:14px}
article.post .lead{font-size:1.12rem;color:var(--ink-soft);line-height:1.75;margin:18px 0 28px}
article.post h2{font-family:'DM Serif Display',serif;font-weight:400;font-size:1.65rem;line-height:1.2;margin:44px 0 14px}
article.post p{margin-bottom:16px;font-size:16.5px;line-height:1.8}
article.post ul{margin:0 0 18px 22px}
article.post li{margin-bottom:8px;font-size:16.5px;line-height:1.7}
article.post strong{font-weight:600}
article.post a.inl{color:#9A6424;text-decoration:underline;text-underline-offset:3px}
.tip{background:var(--amber-pale);border-left:4px solid var(--amber);border-radius:8px;padding:18px 20px;margin:22px 0}
.tip p:last-child{margin-bottom:0}
.post-cta{background:var(--ink);color:#fff;border-radius:16px;padding:34px 30px;margin-top:48px;text-align:center}
.post-cta h2{color:#fff;margin:0 0 10px!important}
.post-cta p{color:rgba(255,255,255,.8);max-width:52ch;margin:0 auto 22px!important}
.post-cta .btns{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.post-cta a{display:inline-block;padding:13px 24px;border-radius:var(--r);font-weight:600;font-size:15px}
.post-cta a.b1{background:var(--amber);color:#fff}
.post-cta a.b2{border:1.5px solid rgba(255,255,255,.35);color:#fff}
@media(max-width:560px){article.post{padding:36px 16px 64px}.post-card{padding:22px 18px}.blog-hero{padding:44px 0 24px}}
@media(max-width:980px){.nav-links{display:none}}
@media(max-width:900px){
  .hero-inner,.about-grid,.contact-inner{grid-template-columns:1fr;gap:40px}
  .hero-photo{display:none}
  .why-grid{grid-template-columns:1fr 1fr}
  .pkg-grid,.pkg-extras,.cases-grid,.case.has-img{grid-template-columns:1fr}
  .case.has-img{gap:20px}
  .steps{grid-template-columns:1fr 1fr}
  .step::after{display:none}
  .why,.pakete,.ablauf,.cases,.about,.faq,.contact{padding:64px 0}
}
@media(max-width:560px){
  .wrap{padding:0 16px}
  .why-grid,.steps{grid-template-columns:1fr}
  .hero{padding:52px 0 44px}
  .metrics-inner{flex-direction:column;gap:18px}
  .cta-nav{display:none}
  .about-card{position:static;margin-top:14px}
}
"""

ICON = {
    "chat": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z"/></svg>',
    "hand": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M8 13h8M8 17h5"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 5-6"/></svg>',
    "wa": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12a9 9 0 0 1-13.4 7.9L3 21l1.2-4.4A9 9 0 1 1 21 12z"/><path d="M9 9.5c.3 2.2 2.3 4.2 4.5 4.5l1-1.2 2 .9c-.3 1.2-1.3 1.8-2.4 1.6A6.5 6.5 0 0 1 8.4 10c-.2-1.1.4-2.1 1.6-2.4l.9 2z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M22 6l-10 7L2 6"/></svg>',
    "g": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M21.6 12.2c0-.7-.1-1.3-.2-1.9H12v3.7h5.4a4.6 4.6 0 0 1-2 3v2.5h3.2c1.9-1.7 3-4.3 3-7.3z"/><path d="M12 22c2.7 0 5-.9 6.6-2.4l-3.2-2.5c-.9.6-2 1-3.4 1-2.6 0-4.8-1.8-5.6-4.1H3.1v2.6A10 10 0 0 0 12 22z"/><path d="M6.4 14a6 6 0 0 1 0-3.9V7.5H3.1a10 10 0 0 0 0 9z"/><path d="M12 5.9c1.5 0 2.8.5 3.8 1.5l2.9-2.9A10 10 0 0 0 3.1 7.5l3.3 2.6C7.2 7.700 9.400 5.900 12 5.900z"/></svg>',
    "in": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>',
}

# ---------------------------------------------------------------- ТЕКСТЫ
T = {}

T["de"] = dict(
    title="Webseite & Google-Profil für Selbstständige | Olha Polishchuk",
    desc="Onepager-Webseite und Google-Maps-Profil für Selbstständige und kleine Studios in ganz Deutschland. Beratung auf Ukrainisch oder Russisch, Webseite auf Deutsch.",
    og_title="Webseite & Google-Profil für Selbstständige · Olha Polishchuk",
    nav=["Pakete", "Ablauf", "Ergebnisse", "Über mich", "Kontakt"],
    cta_nav="Kostenloser Google-Check",
    eyebrow="Düsseldorf · NRW · deutschlandweit remote",
    h1="Webseite und Google-Unternehmensprofil für Selbstständige und kleine Betriebe in Deutschland",
    claim="Ihre Kunden suchen Sie in Google. Ich sorge dafür, dass sie Sie <em>finden</em>.",
    sub="Google-Unternehmensprofil, Onepager-Webseite und laufende Betreuung für kleine Unternehmen in Deutschland. Wir sprechen Ukrainisch oder Russisch — Ihre Webseite und alle Texte für Ihre Kunden sind auf Deutsch, klar und korrekt.",
    btn1="Kostenloser Google-Check →", btn2="Pakete & Preise",
    photo_alt="Olha Polishchuk — Webseiten und Google-Profile für Beauty-Studios",
    badge_num="Nr. 1", badge_lbl="in Google für einen Kunden",
    metrics=[("UA · RU", "Beratung — Webseite auf Deutsch"), ("Google SEO", "praktische Erfahrung"), ("Ganz Deutschland", "remote und in Düsseldorf")],
    why_label="Warum mit mir", why_title="Einfach, verständlich — in Ihrer Sprache",
    why=[("chat", "Wir sprechen dieselbe Sprache", "Sie erklären auf Ukrainisch oder Russisch, Ihre Kunden lesen alles auf Deutsch. Ohne Dolmetscher, ohne Missverständnisse."),
         ("hand", "Ich mache das für Sie", "Sie schicken Fotos und ein paar Sätze zu Ihrer Arbeit — den Rest übernehme ich. Sie prüfen nur und sagen „Ja“."),
         ("doc", "Alles schriftlich", "Preis, Umfang und Termine stehen vorab im Angebot. Keine Überraschungen auf der Rechnung."),
         ("chart", "In der Praxis erprobt", "Was ich Kunden anbiete, teste ich zuerst in eigenen Projekten — und sehe das Ergebnis in Zahlen.")],
    pk_label="Pakete & Preise", pk_title="Klare Preise — ohne Überraschungen", pk_btn="Anfragen",
    pk=[dict(tag="Einmalig", name="A · „Man findet Sie in Google“", price='<s class="old">190 €</s> 150 €',
             start="<strong>Startpreis für die ersten 3 Kunden: 150 €</strong> — gegen eine kurze schriftliche Bewertung",
             desc="Ihr Unternehmensprofil in Google Maps — neu eingerichtet oder aufgeräumt:",
             items=["passende Kategorien und Leistungen, Beschreibung auf Deutsch (und Ukrainisch / Russisch)",
                    "Fotos, Öffnungszeiten, Kontakt, Link zu WhatsApp oder Webseite",
                    "die ersten 3 Beiträge im Profil",
                    "QR-Code und fertige Nachricht, um Kundenbewertungen zu sammeln",
                    "falls Sie eine Webseite haben: Titel und Beschreibungen der wichtigsten Seiten, Einrichtung der Google Search Console"],
             term="Dauer: ca. 1 Woche."),
        dict(tag="Einmalig", name="B · Onepager-Webseite", price='<s class="old">450 €</s> 350 €',
             start="<strong>Startpreis für die ersten 3 Kunden: 350 €</strong> — gegen eine kurze schriftliche Bewertung",
             desc="Eine Seite mit allem, was zählt:",
             items=["bis zu 8 Bereiche: Leistungen, Preise, Arbeitsfotos, Bewertungen, Karte, Kontakt",
                    "WhatsApp-Button oder Anfrageformular",
                    "auf Deutsch + Ukrainisch oder Russisch",
                    "die Texte schreibe ich aus Ihren Unterlagen",
                    "optimiert fürs Smartphone",
                    "kostenloses Hosting, Anbindung Ihrer Domain, Google Search Console",
                    "2 Korrekturrunden"],
             term="Dauer: 1–2 Wochen, sobald Ihre Unterlagen da sind."),
        dict(tag="Monatlich", name="C · Betreuung", price='<s class="old">290 €</s> 220 € <small>im 1. Monat</small>', feat=True,
             start="<strong>Erster Monat für die ersten 3 Kunden: 220 €</strong>",
             desc="Damit man Sie nicht nur einmal findet, sondern dauerhaft:",
             items=["4 Beiträge pro Monat im Google-Profil",
                    "Antworten auf Bewertungen (Entwurf von mir, Freigabe durch Sie)",
                    "aktuelle Fotos, Öffnungszeiten, Aktionen",
                    "kleine Änderungen an der Webseite",
                    "jeden Monat eine Seite oder Leistung für Google verbessern",
                    "kurzer Monatsbericht: wie viele Menschen Sie gefunden, angerufen oder eine Route geplant haben"],
             term="Mindestens 3 Monate — erste Ergebnisse in Google zeigen sich meist nach 2–3 Monaten.")],
    pk_combo="<strong>A + B zusammen — 590 €</strong> statt 640 €. Google-Profil und Webseite aus einer Hand.",
    pk_addon="<strong>Zusätzlich zur Betreuung: Content für Sie — +190 € pro Monat.</strong> 12 Beiträge im Monat für Instagram, Telegram oder Threads: Texte, einfache Grafiken, Veröffentlichung nach Plan.",
    pk_note="Alle Preise sind Endpreise. Gemäß § 19 UStG wird keine Umsatzsteuer berechnet. Den genauen Leistungsumfang halten wir schriftlich im Angebot fest.",
    st_label="Ablauf", st_title="Vier Schritte — und man sieht Sie",
    steps=[("Kostenloser Google-Check", "Sie schreiben mir, was Sie machen und in welcher Stadt. Ich schaue, wie man Sie in Google gerade sieht, und schicke Ihnen eine kurze Checkliste mit Wachstumspunkten: was schon gut ist, was stört und was sich verbessern lässt."),
           ("Angebot", "Wenn ich das für Sie umsetzen soll, bekommen Sie ein Angebot mit Preis, Umfang und Termin."),
           ("Umsetzung", "Sie schicken Fotos und Infos, ich setze um. Ich zeige Ihnen das Ergebnis, wir nehmen Korrekturen vor."),
           ("Fertig", "Rechnung nach Abschluss. Auf Wunsch geht es mit der Betreuung weiter.")],
    cs_label="Ergebnisse", cs_title="Echte Ergebnisse für echte Unternehmen",
    dm_title="Demo-Design — so kann Ihre Webseite aussehen", dm_sub="Beispiel für ein erfundenes Studio, damit Sie Stil und Aufbau sehen.",
    demos=[dict(wide=True, img="/images/case-feinschliff.jpg", img_alt="Startseite der Demo-Webseite Feinschliff — fiktives Nagelstudio", tag="Demo · fiktives Studio", name="Feinschliff — Beispiel-Webseite für ein Nagelstudio", link="https://german-nail-studio.netlify.app/",
                text="So kann eine Studio-Webseite aussehen: Leistungen und Preise, Studio, Team, Öffnungszeiten und Terminanfrage, optimiert fürs Smartphone. Das Studio ist erfunden — alle Fotos, Bewertungen und Angaben dienen nur als Beispiel.", res=[])],
    
    cases=[dict(wide=True, img="/images/case-jana-nails.jpg", img_alt='Startseite von jana-nails-beauty.de — Webseite des Nagelstudios JANA NAILS & Beauty', tag='Onepager · Online-Terminbuchung · eigene Domain', name='JANA NAILS & Beauty — Webseite für ein Nagelstudio in Düsseldorf-Benrath', link="https://jana-nails-beauty.de/",
                text='Webseite auf Deutsch und Russisch: Leistungen und Preise mit Behandlungsdauer, Arbeitsfotos, Team, Google-Bewertungen, Karte und Kontakt. Online-Terminbuchung über Fresha — Kundinnen wählen Leistung, Nageldesignerin und Uhrzeit selbst, Erinnerungen kommen automatisch. Umzug auf die eigene Domain des Studios, optimiert fürs Smartphone.',
                quote='Ich bin überglücklich mit meiner neuen Website für mein Nagelstudio! Sie ist wunderschön geworden, übersichtlich und genau so, wie ich sie mir gewünscht habe … Eine absolute Herzensempfehlung!', cite='— Jana, Inhaberin von JANA NAILS & Beauty · Google-Bewertung ★★★★★',
                res=[('11 Tage', 'vom Demo bis zum Start auf der Studio-Domain'), ('24/7', 'Online-Termine ohne WhatsApp-Hin-und-Her'), ('2', 'Sprachen: Deutsch und Russisch')]),
           dict(wide=True, tag="Onepager · Domain · Firmen-E-Mail", name="АВ-Концепція — Webseite für ein Ingenieurbüro aus Charkiw", link="https://avkoncepcia.com/",
                text="Onepager mit Portfolio auf Ukrainisch und Englisch — erstellt aus PDFs, alten .doc-Dateien und über 80 Fotos des Kunden. Dazu eigene Domain und Firmen-E-Mail-Adressen mit Weiterleitung. Der Kunde musste nur noch prüfen.",
                res=[("51", "Objekte mit Filter und Suche"), ("279 → 8 MB", "Bilder komprimiert — schnell auf dem Smartphone"), ("2", "Sprachen: Ukrainisch und Englisch")]),
           dict(tag="SEO · Shopify · Düsseldorf", name="Kanelia — Shop für Nageldesign-Bedarf", link="https://kaneliastore.com/",
                text="SEO-Überarbeitung des Shopify-Shops: Produktseiten, Seitenstruktur, lokale Sichtbarkeit. Ergebnisse nach 2–3 Monaten — laut Google Search Console und Shopify.",
                res=[("Nr. 1", "in Google für „nagelsticker kaufen“"), ("4–5 → 65", "Besuche aus Google pro Monat"), ("9 von 11", "ersten Online-Bestellungen kamen über Google")]),
           dict(tag="Eigenes Projekt · Webseite · Pinterest", name="EaseMyFeed — mein eigenes Projekt", link="https://easemyfeed.com/",
                text="Webseite mit 13 Seiten und eigener Domain, Search Console, Pinterest und Instagram — alles selbst umgesetzt. Hier teste ich zuerst, was ich später für Kunden mache.",
                res=[("7.057", "Pinterest-Impressionen in 30 Tagen"), ("+61 %", "zum Vormonat")]),
           dict(tag="Instagram · SMM", name="Katerina Yakovleva — Instagram für eine Finanzberaterin in Düsseldorf", link="https://www.instagram.com/katerynaiakovlieva/",
                text="Komplette Betreuung des Instagram-Accounts: Strategie, Karussells, Reels und Stories, Texte und Veröffentlichung nach Plan. Jeder Beitrag wird vor der Veröffentlichung auf Compliance geprüft.",
                quote='Ich freue mich sehr über die Zusammenarbeit mit Olga! Ich schätze ihre Aufmerksamkeit, ihre Freundlichkeit und die angenehme Kommunikation. Besonders freuen mich die positiven Ergebnisse der Arbeit an meinem beruflichen Instagram-Account, auf dem ich als Finanzberaterin nützliche Informationen teile.', quote_lang='de', cite='— Katerina Y., Finanzberaterin · Google-Bewertung ★★★★★ (aus dem Russischen übersetzt)',
                res=[("2 → 113", "Follower seit Juli 2026")]),
           dict(tag="Telegram · Threads · SMM", name="FinanzGuide GE — Telegram und Threads für ein Team von Finanzberatern", text="Seit August 2026: Markenstimme, visuelles System und eine Compliance-Checkliste (§ 34d/f GewO, Werbekennzeichnung, DSGVO), die jeder Beitrag durchläuft. Content für russisch- und ukrainischsprachige Familien in NRW. Nach der Analyse von 35 Threads-Beiträgen die Strategie umgebaut: konkreter Betrag oder Frist in der ersten Zeile, Threads statt Einzelposts, Frage am Ende. Dazu kostenlose Zuordnung der Anfragen über WhatsApp-Links mit vorausgefülltem Text und ein Vertrags-Tracker in Google Sheets als Lead-Magnet.",
                res=[("39.933", "Aufrufe des besten Beitrags (Threads)")])],
    also="<strong>Außerdem:</strong> Betreuung von Instagram und Telegram, Einrichtung und Optimierung von Shopify-Shops, Texte auf Deutsch, Ukrainisch und Russisch. Schreiben Sie mir — wir besprechen es.",
    ab_label="Über mich", ab_title="Hallo, ich bin Olha", ab_img_alt="Olha Polishchuk am Laptop",
    ab_langs="Beratung auf",
    ab=["Ich lebe in Düsseldorf. Mein Hintergrund sind Programmierung und Datenanalyse — deshalb achte ich nicht nur darauf, dass es gut aussieht, sondern auch auf die Zahlen: wie viele Menschen Sie gefunden haben und was sie danach getan haben.",
        "Wir sprechen Ukrainisch oder Russisch, Ihre Webseite und die Texte für Ihre Kunden sind auf Deutsch. Ich arbeite mit kleinen Unternehmen: Nagel- und Kosmetikstudios, Friseuren, Cafés, Läden, Handwerk und Dienstleistern."],
    fq_label="Häufige Fragen", fq_title="Antworten auf häufige Fragen",
    faq=[("Ich habe Instagram. Wozu noch Google?", "Wer „Maniküre in der Nähe“ oder „Friseur Düsseldorf“ sucht, öffnet Google und Google Maps — nicht Instagram. Ein Google-Profil ist Ihr kostenloses Schild genau dort, wo man Sie gerade sucht."),
         ("Was brauche ich für den Start?", "Ein paar Fotos Ihrer Arbeit, Ihre Leistungen mit Preisen, Adresse und Öffnungszeiten. Fehlt etwas, sage ich Ihnen, wie Sie es schnell erstellen."),
         ("Arbeiten Sie nur in Düsseldorf?", "Nein, deutschlandweit remote. Persönliche Treffen sind in Düsseldorf und Umgebung möglich."),
         ("Wie bezahle ich?", "Per Rechnung nach Abschluss der Arbeit. Ohne Umsatzsteuer — ich bin Kleinunternehmerin nach § 19 UStG."),
         ("Geht die Zusammenarbeit auch nur schriftlich?", "Ja, das ist sogar praktischer: Alles bleibt im Chat oder in der E-Mail, nichts geht verloren.")],
    ct_title="Ihr kostenloser <em>Google-Check</em>",
    ct_sub="Schreiben Sie mir, was Sie machen und in welcher Stadt. Ich schaue mir Ihr Profil und Ihre Webseite an und schicke Ihnen eine kurze Checkliste: was schon gut ist und was Kunden davon abhält, Sie zu finden. Kostenlos und unverbindlich. Antwort innerhalb von 24 Stunden.",
    wa_label="WhatsApp", wa_text="Hallo! Ich interessiere mich für den kostenlosen Google-Check.",
    f_title="Kostenloser Google-Check", f_name="Name", f_mail="E-Mail", f_msg="Was machen Sie und in welcher Stadt?",
    f_ph_name="Ihr Name", f_ph_msg="z. B. Nagelstudio, Düsseldorf-Benrath", f_btn="Google-Check anfordern →",
    f_note="Ihre Angaben gehen nur per E-Mail an mich – zur Beantwortung Ihrer Anfrage.",
    f_alert="Bitte Name und E-Mail ausfüllen.", lang_name="Sprache",
)

T["uk"] = dict(
    title="Сайт-візитка та Google-профіль для майстрів у Німеччині | Ольга Поліщук",
    desc="Сайт-візитка німецькою та профіль у Google Maps для майстрів і самозайнятих по всій Німеччині. Спілкуємося українською або російською, тексти — німецькою.",
    og_title="Сайт-візитка та Google-профіль для майстрів у Німеччині · Ольга Поліщук",
    nav=["Пакети", "Як працюємо", "Результати", "Про мене", "Контакт"],
    cta_nav="Безкоштовний аудит",
    eyebrow="Düsseldorf · NRW · дистанційно по всій Німеччині",
    h1="Сайт-візитка та профіль у Google Maps для майстрів і самозайнятих у Німеччині",
    claim="Клієнти шукають вас у Google. Зроблю так, щоб вони вас <em>знайшли</em>.",
    sub="Допомагаю україно- та російськомовному малому бізнесу в Німеччині: профіль у Google Maps, сайт-візитка та регулярна підтримка. Спілкуємося українською або російською — тексти для ваших клієнтів пишу грамотною німецькою.",
    btn1="Отримати безкоштовний аудит у Google →", btn2="Пакети та ціни",
    photo_alt="Ольга Поліщук — Google-профіль, сайти та SEO в Дюссельдорфі",
    badge_num="№ 1", badge_lbl="у Google для клієнта",
    metrics=[("UA · RU", "спілкуємося — сайт німецькою"), ("Google SEO", "практичний досвід"), ("Уся Німеччина", "дистанційно та в Düsseldorf")],
    why_label="Чому зі мною зручно", why_title="Просто, зрозуміло й вашою мовою",
    why=[("chat", "Говоримо однією мовою", "Ви пояснюєте українською чи російською, я пишу для ваших клієнтів німецькою. Без перекладача й без непорозумінь."),
         ("hand", "Роблю за вас", "Ви надсилаєте фото й кілька слів про свою роботу — решта на мені. Від вас потрібно лише перевірити й сказати «так»."),
         ("doc", "Усе письмово", "Ціна, обсяг і терміни — заздалегідь у пропозиції. Жодних сюрпризів у рахунку."),
         ("chart", "Перевірено на практиці", "Те, що пропоную клієнтам, спершу роблю для власних проєктів і бачу результат у цифрах.")],
    pk_label="Пакети та ціни", pk_title="Зрозумілі ціни — без сюрпризів", pk_btn="Обговорити",
    pk=[dict(tag="Разово", name="A · «Вас знаходять у Google»", price='<s class="old">190 €</s> 150 €',
             start="<strong>Стартова ціна для перших 3 клієнтів: 150 €</strong> — в обмін на короткий письмовий відгук",
             desc="Профіль вашої компанії в Google Maps — створю з нуля або наведу лад:",
             items=["правильні категорії та послуги, опис німецькою (і українською / російською)",
                    "фото, години роботи, контакти, посилання на WhatsApp або сайт",
                    "3 перші публікації в профілі",
                    "QR-код і готове повідомлення, щоб збирати відгуки клієнтів",
                    "якщо у вас є сайт — заголовки й описи головних сторінок, підключення Google Search Console"],
             term="Термін: близько 1 тижня."),
        dict(tag="Разово", name="B · Сайт-візитка", price='<s class="old">450 €</s> 350 €',
             start="<strong>Стартова ціна для перших 3 клієнтів: 350 €</strong> — в обмін на короткий письмовий відгук",
             desc="Одна сторінка, на якій є все головне:",
             items=["до 8 розділів: послуги, ціни, фото робіт, відгуки, мапа, контакти",
                    "кнопка WhatsApp або форма заявки",
                    "німецькою + українською або російською",
                    "тексти пишу сама з ваших матеріалів",
                    "зручно переглядати з телефона",
                    "безкоштовний хостинг, підключення вашого домену, Google Search Console",
                    "2 кола правок"],
             term="Термін: 1–2 тижні після того, як отримаю ваші матеріали."),
        dict(tag="Щомісяця", name="C · Підтримка", price='<s class="old">290 €</s> 220 € <small>перший місяць</small>', feat=True,
             start="<strong>Перший місяць для перших 3 клієнтів: 220 €</strong>",
             desc="Щоб вас не просто знайшли один раз, а знаходили постійно:",
             items=["4 публікації на місяць у профілі Google",
                    "відповіді на відгуки (надсилаю чернетку, ви погоджуєте)",
                    "оновлення фото, годин роботи, акцій",
                    "дрібні правки сайту",
                    "щомісяця покращую для Google одну сторінку або послугу",
                    "короткий звіт раз на місяць: скільки людей вас знайшли, зателефонували, проклали маршрут"],
             term="Мінімум 3 місяці — перші результати в Google зазвичай видно через 2–3 місяці.")],
    pk_combo="<strong>A + B разом — 590 €</strong> замість 640 €. Google-профіль і сайт в одних руках. Сайт-візитка для майстра манікюру — <a class=\"inl\" href=\"/uk/sait-vizytka-dlia-maistra-manikiuru.html\">детально →</a>",
    pk_addon="<strong>Додатково до підтримки: контент за вас — +190 € на місяць.</strong> 12 дописів на місяць для Instagram, Telegram або Threads: тексти, прості картинки, публікація за розкладом.",
    pk_note="Ціни остаточні: як Kleinunternehmer за § 19 UStG я не нараховую ПДВ. Точний обсяг робіт фіксуємо письмово в пропозиції.",
    st_label="Як ми працюємо", st_title="Чотири кроки — і вас видно",
    steps=[("Безкоштовний аудит", "Ви пишете, чим займаєтеся і в якому місті. Я дивлюся, як вас зараз видно в Google, і надсилаю короткий чек-лист точок зростання: що вже добре, що заважає і що можна покращити."),
           ("Пропозиція", "Якщо хочете, щоб я зробила це за вас, — надсилаю пропозицію з ціною, обсягом і терміном."),
           ("Робота", "Ви надсилаєте фото й інформацію, я роблю. Показую результат, вносимо правки."),
           ("Готово", "Рахунок — після виконання. Якщо потрібно — далі підтримка.")],
    cs_label="Результати", cs_title="Реальні результати для реального бізнесу",
    dm_title="Демо-дизайн — так може виглядати ваш сайт", dm_sub="Приклад для вигаданої студії, щоб ви побачили стиль і структуру.",
    demos=[dict(wide=True, img="/images/case-feinschliff.jpg", img_alt="Головна сторінка демо-сайту Feinschliff — вигадана нейл-студія", tag="Демо · вигадана студія", name="Feinschliff — приклад сайту для нейл-студії", link="https://german-nail-studio.netlify.app/",
                text="Так може виглядати сайт студії: послуги й ціни, студія, команда, години роботи та запис, зручно на смартфоні. Студія вигадана — усі фото, відгуки й дані лише для прикладу.", res=[])],
    
    cases=[dict(wide=True, img="/images/case-jana-nails.jpg", img_alt='Головна сторінка jana-nails-beauty.de — сайт нейл-студії JANA NAILS & Beauty', tag='Сайт-візитка · онлайн-запис · власний домен', name='JANA NAILS & Beauty — сайт нейл-студії в Düsseldorf-Benrath', link="https://jana-nails-beauty.de/",
                text='Сайт німецькою та російською: послуги й прайс із тривалістю процедур, фото робіт, команда, відгуки з Google, мапа й контакти. Онлайн-запис через Fresha — клієнтки самі обирають послугу, майстриню й час, нагадування надходять автоматично. Перенесення на власний домен студії та зручна мобільна версія.',
                quote='Ich bin überglücklich mit meiner neuen Website für mein Nagelstudio! Sie ist wunderschön geworden, übersichtlich und genau so, wie ich sie mir gewünscht habe … Eine absolute Herzensempfehlung!', cite='— Яна, власниця JANA NAILS & Beauty · відгук у Google ★★★★★',
                res=[('11 днів', 'від демоверсії до запуску на домені студії'), ('24/7', 'онлайн-запис без листування у WhatsApp'), ('2', 'мови: німецька та російська')]),
           dict(wide=True, tag="Сайт-візитка · домен · корпоративна пошта", name="«АВ-Концепція» — сайт інженерної компанії (Харків)", link="https://avkoncepcia.com/",
                text="Сайт-візитка з портфоліо українською та англійською — зібраний із PDF, старих .doc-файлів і 80+ фото замовника. Плюс власний домен і корпоративні адреси пошти з переадресацією. Клієнт лише перевіряв.",
                res=[("51", "об'єкт із фільтрами й пошуком"), ("279 → 8 МБ", "фото стиснуто — сайт швидко відкривається з телефона"), ("2", "мови: українська та англійська")]),
           dict(tag="SEO · Shopify · Düsseldorf", name="Kanelia — магазин матеріалів для манікюру", link="https://kaneliastore.com/",
                text="SEO-переробка Shopify-магазину: картки товарів, структура сайту, локальна видимість. Результати через 2–3 місяці — за даними Google Search Console і Shopify.",
                res=[("№ 1", "у Google за запитом «nagelsticker kaufen»"), ("4–5 → 65", "візитів із Google на місяць"), ("9 з 11", "перших онлайн-замовлень — із Google")]),
           dict(tag="Власний проєкт · Сайт · Pinterest", name="EaseMyFeed — мій власний проєкт", link="https://easemyfeed.com/",
                text="Сайт на 13 сторінок із власним доменом, Search Console, Pinterest та Instagram — усе зроблено самостійно. Тут я спершу перевіряю те, що потім роблю для клієнтів.",
                res=[("7 057", "показів у Pinterest за 30 днів"), ("+61 %", "до минулого місяця")]),
           dict(tag="Instagram · SMM", name="Катерина Яковлева — Instagram фінансової консультантки в Düsseldorf", link="https://www.instagram.com/katerynaiakovlieva/",
                text="Голос бренду, візуальна система та регулярні публікації для україно- та російськомовної аудиторії в NRW: стратегія, каруселі, Reels і Stories, тексти та публікація за планом.",
                quote='Очень рада сотрудничеству с Ольгой! Ценю её внимательное отношение, доброжелательность и приятное общение. Особенно радуют положительные результаты работы над моим профессиональным Instagram, где я делюсь полезной информацией как финансовый консультант.', quote_lang='ru', cite='— Екатерина Я., фінансова консультантка · відгук у Google ★★★★★ (мовою оригіналу)',
                res=[("2 → 113", "підписників з липня 2026")]),
           dict(tag="Telegram · Threads · SMM", name="FinanzGuide GE — Telegram і Threads для команди фінансових консультантів", text="З серпня 2026: голос бренду, візуальна система й чек-лист комплаєнсу (§ 34d/f GewO, маркування реклами, DSGVO), через який проходить кожна публікація. Контент для україно- та російськомовних родин у NRW. Після розбору 35 публікацій у Threads перебудувала стратегію: конкретна сума або термін у першому рядку, треди замість поодиноких дописів, запитання наприкінці. А також безкоштовна атрибуція через WhatsApp-посилання з готовим текстом і трекер договорів у Google Sheets як лід-магніт.",
                res=[("39 933", "переглядів найкращого допису"), ("×6", "охоплення з цифрою в першому рядку"), ("×2", "треди проти поодиноких дописів")])],
    also="<strong>Також можу допомогти:</strong> ведення Instagram і Telegram, налаштування й оптимізація Shopify-магазинів, тексти німецькою, українською та російською. Напишіть — обговоримо.",
    ab_label="Про мене", ab_title="Привіт, я Ольга", ab_img_alt="Ольга Поліщук за ноутбуком",
    ab_langs="Спілкуємося",
    ab=["Живу в Düsseldorf. За освітою й досвідом — програмування та аналіз даних, тому дивлюся не лише на «гарно», а й на цифри: скільки людей вас знайшли і що вони зробили далі.",
        "Спілкуємося українською або російською, а сайт і тексти для ваших клієнтів — німецькою. Працюю з невеликими бізнесами: майстрами, салонами, кафе, магазинами, ремонтом і послугами."],
    fq_label="Часті запитання", fq_title="Відповіді на часті запитання",
    faq=[("У мене є Instagram. Навіщо ще Google?", "Коли людина шукає «манікюр поруч» або «Friseur Düsseldorf», вона відкриває Google і Google Maps, а не Instagram. Профіль у Google — це безкоштовна вивіска там, де вас шукають саме зараз."),
         ("Скільки коштує сайт для майстра манікюру?", "Сайт-візитка німецькою — 350 € для перших 3 клієнтів, далі 450 €. Разом із профілем у Google Maps — 590 €. Термін — 1–2 тижні після ваших матеріалів.", "/uk/sait-vizytka-dlia-maistra-manikiuru.html", "Детально →"),
         ("Що мені потрібно для початку?", "Кілька фото вашої роботи, список послуг із цінами, адреса й години роботи. Якщо чогось немає — підкажу, як швидко це зробити."),
         ("Ви працюєте лише в Düsseldorf?", "Ні, дистанційно по всій Німеччині. Зустрітися особисто можу в Düsseldorf і поруч."),
         ("Як оплачувати?", "За рахунком (Rechnung) після виконання роботи. Без ПДВ — я Kleinunternehmer за § 19 UStG."),
         ("Чи можна спілкуватися лише письмово?", "Так, так навіть зручніше: усе залишається в листуванні, і нічого не забувається.")],
    ct_title="Отримайте безкоштовний <em>аудит</em> у Google",
    ct_sub="Напишіть, чим ви займаєтеся і в якому місті. Я подивлюся ваш профіль і сайт та надішлю короткий чек-лист точок зростання: що вже добре і що заважає клієнтам вас знайти. Безкоштовно й без зобов'язань. Відповідаю протягом 24 годин.",
    wa_label="WhatsApp", wa_text="Добрий день! Хочу безкоштовний аудит у Google.",
    f_title="Безкоштовний аудит", f_name="Ім'я", f_mail="E-Mail", f_msg="Чим ви займаєтеся і в якому місті?",
    f_ph_name="Ваше ім'я", f_ph_msg="Наприклад: манікюр, Düsseldorf-Benrath", f_btn="Отримати безкоштовний аудит →",
    f_note="Ваші дані надходять лише мені на e-mail — щоб відповісти на запит.",
    f_alert="Будь ласка, заповніть ім'я та e-mail.", lang_name="Мова",
)

T["ru"] = dict(
    title="Сайт-визитка и Google-профиль для мастеров в Германии | Ольга Полищук",
    desc="Сайт-визитка на немецком и профиль в Google Maps для мастеров и самозанятых по всей Германии. Общаемся по-русски или по-украински, тексты — на немецком.",
    og_title="Сайт-визитка и Google-профиль для мастеров в Германии · Ольга Полищук",
    nav=["Пакеты", "Как работаем", "Результаты", "Обо мне", "Контакт"],
    cta_nav="Бесплатный аудит",
    eyebrow="Düsseldorf · NRW · по всей Германии удалённо",
    h1="Сайт-визитка и профиль в Google Maps для мастеров и самозанятых в Германии",
    claim="Клиенты ищут вас в Google. Сделаю так, чтобы они вас <em>нашли</em>.",
    sub="Помогаю русско- и украиноязычному малому бизнесу в Германии: профиль в Google Maps, сайт-визитка и регулярная поддержка. Общаемся по-русски или по-украински — тексты для ваших клиентов пишу на грамотном немецком.",
    btn1="Получить бесплатный аудит в Google →", btn2="Пакеты и цены",
    photo_alt="Ольга Полищук — Google-профиль, сайты и SEO в Дюссельдорфе",
    badge_num="№ 1", badge_lbl="в Google для клиента",
    metrics=[("RU · UA", "общаемся — сайт на немецком"), ("Google SEO", "практический опыт"), ("Вся Германия", "удалённо и в Düsseldorf")],
    why_label="Почему со мной удобно", why_title="Просто, понятно и на вашем языке",
    why=[("chat", "Говорим на одном языке", "Вы объясняете по-русски или по-украински, я пишу для ваших клиентов по-немецки. Без переводчика и без недопонимания."),
         ("hand", "Делаю за вас", "Вы присылаете фото и пару слов о своей работе — остальное на мне. От вас нужно только проверить и сказать «да»."),
         ("doc", "Всё письменно", "Цена, объём и сроки — заранее в предложении. Никаких сюрпризов в счёте."),
         ("chart", "Проверено на практике", "То, что предлагаю клиентам, сначала делаю для своих проектов и вижу результат в цифрах.")],
    pk_label="Пакеты и цены", pk_title="Понятные цены — без сюрпризов", pk_btn="Обсудить",
    pk=[dict(tag="Разово", name="A · «Вас находят в Google»", price='<s class="old">190 €</s> 150 €',
             start="<strong>Стартовая цена для первых 3 клиентов: 150 €</strong> — в обмен на короткий письменный отзыв",
             desc="Профиль вашей компании в Google Maps — создам с нуля или приведу в порядок:",
             items=["правильные категории и услуги, описание на немецком (и на русском / украинском)",
                    "фото, часы работы, контакты, ссылка на WhatsApp или сайт",
                    "3 первые публикации в профиле",
                    "QR-код и готовое сообщение, чтобы собирать отзывы клиентов",
                    "если у вас есть сайт — заголовки и описания главных страниц, подключение Google Search Console"],
             term="Срок: около 1 недели."),
        dict(tag="Разово", name="B · Сайт-визитка", price='<s class="old">450 €</s> 350 €',
             start="<strong>Стартовая цена для первых 3 клиентов: 350 €</strong> — в обмен на короткий письменный отзыв",
             desc="Одна страница, на которой есть всё главное:",
             items=["до 8 разделов: услуги, цены, фото работ, отзывы, карта, контакты",
                    "кнопка WhatsApp или форма заявки",
                    "на немецком + русском или украинском",
                    "тексты пишу сама из ваших материалов",
                    "удобно смотреть с телефона",
                    "бесплатный хостинг, подключение вашего домена, Google Search Console",
                    "2 круга правок"],
             term="Срок: 1–2 недели после того, как получу ваши материалы."),
        dict(tag="Каждый месяц", name="C · Поддержка", price='<s class="old">290 €</s> 220 € <small>первый месяц</small>', feat=True,
             start="<strong>Первый месяц для первых 3 клиентов: 220 €</strong>",
             desc="Чтобы вас не просто нашли один раз, а находили постоянно:",
             items=["4 публикации в месяц в профиле Google",
                    "ответы на отзывы (присылаю черновик, вы согласуете)",
                    "обновление фото, часов, акций",
                    "мелкие правки сайта",
                    "каждый месяц улучшаю для Google одну страницу или услугу",
                    "короткий отчёт раз в месяц: сколько людей вас нашли, позвонили, проложили маршрут"],
             term="Минимум 3 месяца — первые результаты в Google обычно видны через 2–3 месяца.")],
    pk_combo="<strong>A + B вместе — 590 €</strong> вместо 640 €. Google-профиль и сайт в одних руках. Сайт-визитка для мастера маникюра — <a class=\"inl\" href=\"/ru/sait-vizitka-dlya-mastera-manikyura.html\">подробно →</a>",
    pk_addon="<strong>Дополнительно к поддержке: контент за вас — +190 € в месяц.</strong> 12 постов в месяц для Instagram, Telegram или Threads: тексты, простые картинки, публикация по расписанию.",
    pk_note="Цены окончательные: как Kleinunternehmer по § 19 UStG я не начисляю НДС. Точный объём работ фиксируем письменно в предложении.",
    st_label="Как мы работаем", st_title="Четыре шага — и вас видно",
    steps=[("Бесплатный аудит", "Вы пишете, чем занимаетесь и в каком городе. Я смотрю, как вас сейчас видно в Google, и присылаю короткий чек-лист точек роста: что уже хорошо, что мешает и что можно улучшить."),
           ("Предложение", "Если хотите, чтобы я сделала это за вас, — присылаю предложение с ценой, объёмом и сроком."),
           ("Работа", "Вы присылаете фото и информацию, я делаю. Показываю результат, вносим правки."),
           ("Готово", "Счёт после выполнения. Если нужно — дальше поддержка.")],
    cs_label="Результаты", cs_title="Реальные результаты для реального бизнеса",
    dm_title="Демо-дизайн — так может выглядеть ваш сайт", dm_sub="Пример для вымышленной студии, чтобы вы увидели стиль и структуру.",
    demos=[dict(wide=True, img="/images/case-feinschliff.jpg", img_alt="Главная страница демо-сайта Feinschliff — вымышленная ногтевая студия", tag="Демо · вымышленная студия", name="Feinschliff — пример сайта для ногтевой студии", link="https://german-nail-studio.netlify.app/",
                text="Так может выглядеть сайт студии: услуги и цены, студия, команда, часы работы и запись, удобно на смартфоне. Студия вымышленная — все фото, отзывы и данные только для примера.", res=[])],
    
    cases=[dict(wide=True, img="/images/case-jana-nails.jpg", img_alt='Главная страница jana-nails-beauty.de — сайт ногтевой студии JANA NAILS & Beauty', tag='Сайт-визитка · онлайн-запись · свой домен', name='JANA NAILS & Beauty — сайт ногтевой студии в Düsseldorf-Benrath', link="https://jana-nails-beauty.de/",
                text='Сайт на немецком и русском: услуги и прайс с длительностью процедур, фото работ, команда, отзывы из Google, карта и контакты. Онлайн-запись через Fresha — клиентки сами выбирают услугу, мастера и время, напоминания приходят автоматически. Перенос на собственный домен студии и удобная мобильная версия.',
                quote='Ich bin überglücklich mit meiner neuen Website für mein Nagelstudio! Sie ist wunderschön geworden, übersichtlich und genau so, wie ich sie mir gewünscht habe … Eine absolute Herzensempfehlung!', cite='— Яна, владелица JANA NAILS & Beauty · отзыв в Google ★★★★★',
                res=[('11 дней', 'от демо-версии до запуска на домене студии'), ('24/7', 'онлайн-запись без переписки в WhatsApp'), ('2', 'языка: немецкий и русский')]),
           dict(wide=True, tag="Сайт-визитка · домен · корпоративная почта", name="«АВ-Концепція» — сайт инженерной компании (Харьков)", link="https://avkoncepcia.com/",
                text="Сайт-визитка с портфолио на украинском и английском — собран из PDF, старых .doc-файлов и 80+ фото заказчика. Плюс свой домен и корпоративные адреса почты с переадресацией. Клиент только проверял.",
                res=[("51", "объект с фильтрами и поиском"), ("279 → 8 МБ", "фото сжаты — сайт быстро открывается с телефона"), ("2", "языка: украинский и английский")]),
           dict(tag="SEO · Shopify · Düsseldorf", name="Kanelia — магазин материалов для маникюра", link="https://kaneliastore.com/",
                text="SEO-переработка Shopify-магазина: карточки товаров, структура сайта, локальная видимость. Результаты через 2–3 месяца — по данным Google Search Console и Shopify.",
                res=[("№ 1", "в Google по запросу «nagelsticker kaufen»"), ("4–5 → 65", "визитов из Google в месяц"), ("9 из 11", "первых онлайн-заказов — из Google")]),
           dict(tag="Свой проект · Сайт · Pinterest", name="EaseMyFeed — мой собственный проект", link="https://easemyfeed.com/",
                text="Сайт на 13 страниц со своим доменом, Search Console, Pinterest и Instagram — всё сделано самостоятельно. Здесь я сначала проверяю то, что потом делаю для клиентов.",
                res=[("7 057", "показов в Pinterest за 30 дней"), ("+61 %", "к прошлому месяцу")]),
           dict(tag="Instagram · SMM", name="Катерина Яковлева — Instagram финансового консультанта в Düsseldorf", link="https://www.instagram.com/katerynaiakovlieva/",
                text="Голос бренда, визуальная система и регулярные публикации для русско- и украиноязычной аудитории в NRW: стратегия, карусели, Reels и Stories, тексты и публикация по плану.",
                quote='Очень рада сотрудничеству с Ольгой! Ценю её внимательное отношение, доброжелательность и приятное общение. Особенно радуют положительные результаты работы над моим профессиональным Instagram, где я делюсь полезной информацией как финансовый консультант.', quote_lang='ru', cite='— Екатерина Я., финансовый консультант · отзыв в Google ★★★★★',
                res=[("2 → 113", "подписчиков с июля 2026")]),
           dict(tag="Telegram · Threads · SMM", name="FinanzGuide GE — Telegram и Threads для команды финансовых консультантов", text="С августа 2026: голос бренда, визуальная система и чек-лист комплаенса (§ 34d/f GewO, маркировка рекламы, DSGVO), через который проходит каждая публикация. Контент для русско- и украиноязычных семей в NRW. После разбора 35 публикаций в Threads перестроила стратегию: конкретная сумма или срок в первой строке, треды вместо одиночных постов, вопрос в конце. Плюс бесплатная атрибуция через WhatsApp-ссылки с предзаполненным текстом и трекер договоров в Google Sheets как лид-магнит.",
                res=[("39 933", "просмотра у лучшего поста"), ("×6", "охват с цифрой в первой строке"), ("×2", "треды против одиночных постов")])],
    also="<strong>Также могу помочь:</strong> ведение Instagram и Telegram, настройка и оптимизация Shopify-магазинов, тексты на немецком, русском и украинском. Напишите — обсудим.",
    ab_label="Обо мне", ab_title="Привет, я Ольга", ab_img_alt="Ольга Полищук за ноутбуком",
    ab_langs="Общаемся",
    ab=["Живу в Düsseldorf. По образованию и опыту — программирование и анализ данных, поэтому смотрю не только на «красиво», но и на цифры: сколько людей вас нашли и что они сделали дальше.",
        "Общаемся по-русски или по-украински, а сайт и тексты для ваших клиентов — на немецком. Работаю с небольшими бизнесами: мастерами, салонами, кафе, магазинами, ремонтом и услугами."],
    fq_label="Частые вопросы", fq_title="Ответы на частые вопросы",
    faq=[("У меня есть Instagram. Зачем ещё Google?", "Когда человек ищет «маникюр рядом» или «Friseur Düsseldorf», он открывает Google и Google Maps, а не Instagram. Профиль в Google — это бесплатная вывеска там, где вас ищут прямо сейчас."),
         ("Сколько стоит сайт для мастера маникюра?", "Сайт-визитка на немецком — 350 € для первых 3 клиентов, дальше 450 €. Вместе с профилем в Google Maps — 590 €. Срок — 1–2 недели после ваших материалов.", "/ru/sait-vizitka-dlya-mastera-manikyura.html", "Подробно →"),
         ("Что мне нужно для начала?", "Пару фото вашей работы, список услуг с ценами, адрес и часы работы. Если чего-то нет — подскажу, как быстро сделать."),
         ("Вы работаете только в Düsseldorf?", "Нет, по всей Германии удалённо. Встретиться лично могу в Düsseldorf и рядом."),
         ("Как оплачивать?", "По счёту (Rechnung) после выполнения работы. Без НДС — я Kleinunternehmer по § 19 UStG."),
         ("Можно ли общаться только письменно?", "Да, так даже удобнее: всё остаётся в переписке, и ничего не забывается.")],
    ct_title="Получите бесплатный <em>аудит</em> в Google",
    ct_sub="Напишите, чем вы занимаетесь и в каком городе. Я посмотрю ваш профиль и сайт и пришлю короткий чек-лист точек роста: что уже хорошо и что мешает клиентам вас найти. Бесплатно и без обязательств. Отвечаю в течение 24 часов.",
    wa_label="WhatsApp", wa_text="Здравствуйте! Хочу бесплатный аудит в Google.",
    f_title="Бесплатный аудит", f_name="Имя", f_mail="E-Mail", f_msg="Чем вы занимаетесь и в каком городе?",
    f_ph_name="Ваше имя", f_ph_msg="Например: маникюр, Düsseldorf-Benrath", f_btn="Получить бесплатный аудит →",
    f_note="Ваши данные приходят только мне на e-mail — чтобы ответить на запрос.",
    f_alert="Пожалуйста, заполните имя и e-mail.", lang_name="Язык",
)

# ---- Пазл-лид-магнит в блоке «Обо мне» ----
PZ_SLUG = "checklist-google-maps.html"
PZ = {
    "de": dict(label="Mini-Spiel", title="Puzzle lösen — Geschenk bekommen",
               text="Setzen Sie das Bild zusammen und holen Sie sich Ihr Passwort und eine kostenlose Checkliste für Google Maps.",
               hint="Tippen Sie nacheinander auf zwei Teile, um sie zu tauschen.", moves="Züge", shuffle="Neu mischen",
               m_title="Sie sind super! Das Glück ist heute auf Ihrer Seite 🎉", m_pass="Ihr Passwort", word="ERFOLG",
               m_text="Holen Sie sich die Checkliste „10 Punkte für Ihr Google-Maps-Profil“. Und wenn Sie mir das Passwort per WhatsApp schicken, prüfe ich Ihr Profil bevorzugt.",
               m_btn1="Checkliste öffnen", m_btn2="Passwort per WhatsApp senden", close="Schließen",
               wa="Hallo! Mein Passwort: ERFOLG. Ich möchte einen Check meines Google-Profils.",
               alt="Puzzle: Olha Polishchuk am Laptop"),
    "uk": dict(label="Міні-гра", title="Зберіть картинку — отримайте подарунок",
               text="Складіть пазл і заберіть слово-пароль та безкоштовний чек-лист щодо Google Maps.",
               hint="Натисніть по черзі на два шматочки, щоб поміняти їх місцями.", moves="Ходів", shuffle="Перемішати",
               m_title="Ви супер! Удача сьогодні з вами 🎉", m_pass="Ваше слово-пароль", word="УСПІХ",
               m_text="Забирайте чек-лист «10 перевірок профілю в Google Maps». А якщо назвете пароль у WhatsApp — перевірю ваш профіль позачергово.",
               m_btn1="Відкрити чек-лист", m_btn2="Надіслати пароль у WhatsApp", close="Закрити",
               wa="Добрий день! Мій пароль: УСПІХ. Хочу перевірку профілю в Google.",
               alt="Пазл: Ольга Поліщук за ноутбуком"),
    "ru": dict(label="Мини-игра", title="Соберите картинку — получите подарок",
               text="Сложите пазл и заберите слово-пароль и бесплатный чек-лист по Google Maps.",
               hint="Нажмите по очереди на два кусочка, чтобы поменять их местами.", moves="Ходов", shuffle="Перемешать",
               m_title="Вы супер! Удача сегодня с вами 🎉", m_pass="Ваше слово-пароль", word="УСПЕХ",
               m_text="Забирайте чек-лист «10 проверок профиля в Google Maps». А если назовёте пароль в WhatsApp — проверю ваш профиль вне очереди.",
               m_btn1="Открыть чек-лист", m_btn2="Отправить пароль в WhatsApp", close="Закрыть",
               wa="Здравствуйте! Мой пароль: УСПЕХ. Хочу проверку профиля в Google.",
               alt="Пазл: Ольга Полищук за ноутбуком"),
}

PZ_CSS = r"""
/* PUZZLE */
.pz{margin-top:72px;background:var(--ink);border-radius:18px;padding:40px;display:grid;grid-template-columns:0.9fr 1.1fr;gap:44px;align-items:center;color:#fff}
.pz .sec-label{color:var(--amber-light)}
.pz h3{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(1.5rem,2.6vw,2rem);line-height:1.15;margin-bottom:12px}
.pz-text{color:rgba(255,255,255,0.78);margin-bottom:10px}
.pz-hint{font-size:13px;color:rgba(255,255,255,0.6);margin-bottom:18px}
.pz-bar{display:flex;align-items:center;gap:16px;flex-wrap:wrap;font-size:14px;color:rgba(255,255,255,0.75)}
.pz-btn{background:transparent;border:1px solid rgba(255,255,255,0.3);color:#fff;border-radius:8px;padding:8px 14px;font:inherit;font-size:14px;cursor:pointer}
.pz-btn:hover{border-color:var(--amber-light);color:var(--amber-light)}
.pz-board{display:grid;grid-template-columns:repeat(3,1fr);gap:3px;aspect-ratio:4/3;width:100%;background:rgba(255,255,255,0.08);border-radius:12px;overflow:hidden;touch-action:manipulation}
.pz-tile{border:0;padding:0;cursor:pointer;background-color:#2a375c;background-size:300% 300%;background-repeat:no-repeat;transition:transform .15s,box-shadow .15s,opacity .15s}
.pz-tile:hover{opacity:.92}
.pz-tile:focus-visible{outline:3px solid var(--amber-light);outline-offset:-3px}
.pz-tile.sel{box-shadow:inset 0 0 0 4px var(--amber-light);transform:scale(.96)}
.pz-board.done{gap:0}
.pz-board.done .pz-tile{cursor:default;transform:none;box-shadow:none}
.pz-modal{position:fixed;inset:0;z-index:300;background:rgba(15,20,38,0.72);display:none;align-items:center;justify-content:center;padding:16px}
.pz-modal.open{display:flex}
.pz-dialog{background:#fff;color:var(--ink);border-radius:16px;max-width:440px;width:100%;padding:32px 28px 26px;text-align:center;position:relative;animation:pzIn .3s ease}
@keyframes pzIn{from{opacity:0;transform:translateY(12px) scale(.97)}to{opacity:1;transform:none}}
.pz-x{position:absolute;top:10px;right:12px;background:none;border:0;font-size:24px;line-height:1;color:var(--ink-soft);cursor:pointer;padding:6px}
.pz-dialog h4{font-family:'DM Serif Display',serif;font-weight:400;font-size:1.55rem;line-height:1.2;margin-bottom:16px}
.pz-pass-l{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-soft)}
.pz-word{font-family:'DM Serif Display',serif;font-size:2.3rem;letter-spacing:.12em;color:var(--amber);margin:4px 0 14px}
.pz-dialog p{color:var(--ink-soft);font-size:15px;margin-bottom:20px}
.pz-acts{display:flex;flex-direction:column;gap:10px}
.pz-a1{background:var(--amber);color:#fff;font-weight:600;padding:13px 18px;border-radius:8px}
.pz-a1:hover{background:var(--amber-light)}
.pz-a2{background:#25D366;color:#fff;font-weight:600;padding:13px 18px;border-radius:8px}
.pz-a2:hover{filter:brightness(1.06)}
@media (max-width:860px){.pz{grid-template-columns:1fr;padding:26px 18px;gap:24px;margin-top:56px}}
"""

ANCHORS = ["pakete", "ablauf", "ergebnisse", "about", "contact"]


def esc(s):
    return html.escape(s, quote=True)



def puzzle_html(lang, t):
    from urllib.parse import quote
    z = PZ[lang]
    wa = "https://wa.me/%s?text=%s" % (WA_NUM, quote(z["wa"]))
    img = "/images/puzzle-%s.jpg" % lang
    chk = "/%s%s" % (PATHS[lang], PZ_SLUG)
    o = []
    o.append('  <div class="wrap">\n  <div class="pz" id="puzzle">\n    <div>\n')
    o.append('      <div class="sec-label">%s</div>\n      <h3>%s</h3>\n' % (esc(z["label"]), esc(z["title"])))
    o.append('      <p class="pz-text">%s</p>\n      <p class="pz-hint">%s</p>\n' % (esc(z["text"]), esc(z["hint"])))
    o.append('      <div class="pz-bar"><span>%s: <b id="pz-moves">0</b></span><button type="button" class="pz-btn" id="pz-shuffle">%s</button></div>\n    </div>\n' % (esc(z["moves"]), esc(z["shuffle"])))
    o.append('    <div class="pz-board" id="pz-board" role="group" aria-label="%s" data-img="%s" data-webp="%s"></div>\n  </div>\n  </div>\n' % (esc(z["alt"]), img, img.replace(".jpg", "-1024.webp")))
    o.append('  <div class="pz-modal" id="pz-modal" role="dialog" aria-modal="true" aria-labelledby="pz-mt"><div class="pz-dialog">\n')
    o.append('    <button type="button" class="pz-x" id="pz-close" aria-label="%s">&times;</button>\n' % esc(z["close"]))
    o.append('    <h4 id="pz-mt">%s</h4>\n    <div class="pz-pass-l">%s</div>\n    <div class="pz-word">%s</div>\n' % (esc(z["m_title"]), esc(z["m_pass"]), esc(z["word"])))
    o.append('    <p>%s</p>\n    <div class="pz-acts"><a class="pz-a1" href="%s" data-umami-event="puzzle-checkliste">%s</a><a class="pz-a2" href="%s" target="_blank" rel="noopener" data-umami-event="puzzle-whatsapp">%s</a></div>\n' % (esc(z["m_text"]), chk, esc(z["m_btn1"]), esc(wa), esc(z["m_btn2"])))
    o.append('  </div></div>\n')
    o.append(PZ_JS)
    return "".join(o)


PZ_JS = r"""  <script>
(function(){
  var board=document.getElementById('pz-board'); if(!board) return;
  var movesEl=document.getElementById('pz-moves'), modal=document.getElementById('pz-modal');
  var N=3, order=[], sel=null, moves=0, done=false, tiles=[];
  for(var i=0;i<N*N;i++){
    var b=document.createElement('button'); b.type='button'; b.className='pz-tile';
    b.setAttribute('aria-label',String(i+1)); b.dataset.pos=i;
    b.addEventListener('click',onTap); tiles.push(b); board.appendChild(b);
  }
  function paint(){
    for(var p=0;p<tiles.length;p++){
      var k=order[p], x=k%N, y=Math.floor(k/N);
      tiles[p].style.backgroundPosition=(x*50)+'% '+(y*50)+'%';
      tiles[p].classList.toggle('sel',sel===p);
    }
    movesEl.textContent=moves;
  }
  function solved(){for(var p=0;p<order.length;p++){if(order[p]!==p)return false}return true}
  function shuffle(){
    order=[]; for(var i=0;i<N*N;i++)order.push(i);
    do{for(var j=order.length-1;j>0;j--){var r=Math.floor(Math.random()*(j+1)),t=order[j];order[j]=order[r];order[r]=t}}while(solved());
    sel=null; moves=0; done=false; board.classList.remove('done'); paint();
  }
  function onTap(e){
    if(done) return;
    var p=+e.currentTarget.dataset.pos;
    if(sel===null){sel=p}else if(sel===p){sel=null}else{
      var t=order[sel];order[sel]=order[p];order[p]=t;sel=null;moves++;
      if(solved()){done=true;if(window.umami)umami.track('puzzle-geloest');board.classList.add('done');paint();setTimeout(openM,700);return}
    }
    paint();
  }
  var last=null;
  function openM(){last=document.activeElement;modal.classList.add('open');document.getElementById('pz-close').focus()}
  function closeM(){modal.classList.remove('open');if(last)last.focus()}
  document.getElementById('pz-close').addEventListener('click',closeM);
  modal.addEventListener('click',function(e){if(e.target===modal)closeM()});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&modal.classList.contains('open'))closeM()});
  document.getElementById('pz-shuffle').addEventListener('click',shuffle);
  function load(){var wp=board.dataset.webp&&document.createElement('canvas').toDataURL('image/webp').indexOf('image/webp')===5;var u='url('+(wp?board.dataset.webp:board.dataset.img)+')';tiles.forEach(function(t){t.style.backgroundImage=u})}
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(en){if(en[0].isIntersecting){load();io.disconnect()}},{rootMargin:'400px'});io.observe(board);
  }else load();
  shuffle();
})();
  </script>
"""


def wa_float(lang):
    """Плавающая кнопка WhatsApp — всегда видна в правом нижнем углу (заменила виджет YourGood 08.11.2026)."""
    from urllib.parse import quote
    t = T[lang]
    href = "https://wa.me/%s?text=%s" % (WA_NUM, quote(t["wa_text"]))
    label = {"de": "Per WhatsApp schreiben", "uk": "Написати у WhatsApp", "ru": "Написать в WhatsApp"}[lang]
    return ('<a class="wa-float" href="%s" target="_blank" rel="noopener" aria-label="%s" title="%s" '
            'data-umami-event="whatsapp-float">%s</a>\n' % (html.escape(href, quote=True), label, label, ICON["wa"]))


import re as _re


def _plain(s):
    """HTML → чистый текст для JSON-LD."""
    return html.unescape(_re.sub(r"<[^>]+>", "", s)).strip()


def jsonld(lang, t):
    """Микроразметка Schema.org: бизнес + услуги с ценами + FAQ (для Google, Bing, ИИ-поиска)."""
    url = SITE + PATHS[lang]
    biz_id = SITE + "#business"
    offers = []
    for p in t["pk"]:
        nums = [int(n) for n in _re.findall(r"(\d+)\s*€", p["price"])]
        regular = max(nums)
        spec = {"@type": "UnitPriceSpecification", "price": regular, "priceCurrency": "EUR"}
        if "feat" in p:  # пакет C — помесячно
            spec["unitCode"] = "MON"
        offers.append({"@type": "Offer", "priceSpecification": spec,
                       "itemOffered": {"@type": "Service", "name": _plain(p["name"]),
                                       "description": _plain(p["desc"]) + " " + "; ".join(_plain(i) for i in p["items"])}})
    for key, monthly in (("pk_combo", False), ("pk_addon", True)):
        txt = _plain(t[key])
        m = _re.search(r"(\d+)\s*€", txt)
        if not m:
            continue
        name = _re.split(r"\s[—–-]\s", _re.search(r"<strong>(.*?)</strong>", t[key]).group(1))[0]
        if ":" in name:  # «Дополнительно к поддержке: контент за вас» → «Контент за вас»
            name = name.split(":", 1)[1].strip()
            name = name[:1].upper() + name[1:]
        spec = {"@type": "UnitPriceSpecification", "price": int(m.group(1)), "priceCurrency": "EUR"}
        if monthly:
            spec["unitCode"] = "MON"
        offers.append({"@type": "Offer", "priceSpecification": spec,
                       "itemOffered": {"@type": "Service", "name": _plain(name), "description": txt}})
    same = [LINKEDIN] + ([GBP_URL] if GBP_URL else [])
    biz = {
        "@type": "ProfessionalService",
        "@id": biz_id,
        "name": "Olha Polishchuk",
        "alternateName": "Olha Polishchuk — Google-Profil, Webseite & SEO",
        "description": t["desc"],
        "url": SITE,
        "image": SITE + "images/olha-portrait.jpg",
        "email": EMAIL,
        "address": {"@type": "PostalAddress", "addressLocality": "Düsseldorf", "postalCode": "40589",
                    "addressRegion": "Nordrhein-Westfalen", "addressCountry": "DE"},
        "areaServed": [{"@type": "City", "name": "Düsseldorf"},
                       {"@type": "State", "name": "Nordrhein-Westfalen"},
                       {"@type": "Country", "name": "Deutschland"}],
        "knowsLanguage": ["de", "uk", "ru"],
        "priceRange": "150–590 €",
        "currenciesAccepted": "EUR",
        "founder": {"@type": "Person", "@id": SITE + "#olha", "name": "Olha Polishchuk",
                    "jobTitle": "Google-Profil, Webseiten & SEO", "sameAs": same},
        "sameAs": same,
        **({"hasMap": GBP_URL} if GBP_URL else {}),
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": _plain(t["pk_title"]), "itemListElement": offers},
    }
    page = {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": t["title"],
            "description": t["desc"], "inLanguage": lang, "about": {"@id": biz_id},
            "isPartOf": {"@type": "WebSite", "@id": SITE + "#website", "url": SITE, "name": "Olha Polishchuk",
                         "inLanguage": ["de", "uk", "ru"], "publisher": {"@id": biz_id}}}
    faq = {"@type": "FAQPage", "@id": url + "#faq", "inLanguage": lang,
           "mainEntity": [{"@type": "Question", "name": _plain(q),
                           "acceptedAnswer": {"@type": "Answer", "text": _plain(a)}} for q, a, *_ in t["faq"]]}
    data = {"@context": "https://schema.org", "@graph": [biz, page, faq]}
    js = json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return '<script type="application/ld+json">\n' + js + '\n</script>\n'


# Блог: какие языки уже имеют статьи (DE включён 07.11.2026)
BLOG_LANGS = ("de", "uk", "ru")
BLOG_LABEL = {"de": "Blog", "uk": "Блог", "ru": "Блог"}
MENU_LABEL = {"de": "Menü", "uk": "Меню", "ru": "Меню"}


def header_html(lang, home=True, alt_paths=None, current=None):
    """Шапка с бургер-меню. home=False — ссылки на якоря ведут на главную.
    alt_paths: {lang: путь} для переключателя языков (по умолчанию — главные)."""
    t = T[lang]
    base = "" if home else "/" + PATHS[lang]
    alt = alt_paths or {l2: "/" + PATHS[l2] for l2 in ("de", "uk", "ru")}
    links = [(base + "#" + a, label, None) for a, label in zip(ANCHORS, t["nav"])]
    if lang in BLOG_LANGS:
        links.insert(4, ("/" + PATHS[lang] + "blog/", BLOG_LABEL[lang], "blog"))
    o = []
    w = o.append
    w('<a class="skip" href="#inhalt">%s</a>\n' % SKIP_LABEL[lang])
    w('<header id="hdr">\n  <nav class="wrap" aria-label="Navigation">\n')
    w('    <a class="brand" href="/%s"><span class="brand-init" aria-hidden="true">OP</span><span class="brand-name">Olha <span>Polishchuk</span></span></a>\n' % PATHS[lang])
    w('    <div class="nav-links">\n')
    for href, label, key in links:
        cur = ' class="cur" aria-current="page"' if key and key == current else ''
        w('      <a href="%s"%s>%s</a>\n' % (href, cur, esc(label)))
    w('    </div>\n    <div class="nav-right">\n      <div class="lang-sw" role="group" aria-label="%s">' % esc(t["lang_name"]))
    for l2 in ("uk", "de", "ru"):
        if l2 not in alt:
            continue
        cur = ' class="on" aria-current="true"' if l2 == lang else ''
        w('<a href="%s" hreflang="%s" lang="%s" translate="no"%s>%s</a>' % (alt[l2], l2, l2, cur, LABELS[l2]))
    w('</div>\n      <a href="%s#contact" class="cta-nav">%s</a>\n' % (base, esc(t["cta_nav"])))
    w('      <button class="burger" type="button" aria-label="%s" aria-expanded="false" aria-controls="mnav"><span></span></button>\n' % MENU_LABEL[lang])
    w('    </div>\n  </nav>\n  <div class="mnav" id="mnav">\n    <div class="wrap">\n')
    for href, label, key in links:
        w('      <a class="ml" href="%s">%s</a>\n' % (href, esc(label)))
    w('      <a class="cta-m" href="%s#contact">%s</a>\n    </div>\n  </div>\n</header>\n\n' % (base, esc(t["cta_nav"])))
    return "".join(o)


BURGER_JS = """<script>
(function(){var h=document.getElementById('hdr');if(!h)return;var b=h.querySelector('.burger');
function set(o){h.classList.toggle('open',o);b.setAttribute('aria-expanded',o?'true':'false');}
b.addEventListener('click',function(){set(!h.classList.contains('open'));});
h.querySelectorAll('.mnav a').forEach(function(a){a.addEventListener('click',function(){set(false);});});
document.addEventListener('keydown',function(e){if(e.key==='Escape')set(false);});
window.addEventListener('resize',function(){if(window.innerWidth>980)set(false);});})();
</script>
"""


def footer_html():
    return '<footer>\n  <div class="wrap foot-inner">\n    <div class="foot-copy">© 2026 Olha Polishchuk · Düsseldorf</div>\n    <div class="foot-links"><a href="/impressum.html">Impressum</a><a href="/datenschutz.html">Datenschutz</a>%s<a href="%s" target="_blank" rel="noopener">LinkedIn</a></div>\n  </div>\n</footer>\n\n' % (('<a href="%s" target="_blank" rel="noopener" data-umami-event="footer-google-profil">Google-Profil</a>' % GBP_URL) if GBP_URL else "", LINKEDIN)


FORM_JS = """<script>
(function(){
  var f=document.getElementById('kform'); if(!f) return;
  var st=document.getElementById('kform-status'), ok=document.getElementById('kform-ok'), btn=f.querySelector('.form-submit');
  var t0=Date.now(), label=btn.textContent;
  function fail(n,m,msg){
    var body=encodeURIComponent(msg+"\\n\\nE-Mail: "+m);
    var mailto="mailto:"+%(mail)s+"?subject="+encodeURIComponent("[Website] Google-Check: "+n+" ("+%(label)s+")")+"&body="+body;
    st.className='form-status err';
    st.innerHTML='';
    st.appendChild(document.createTextNode(%(err)s+' '));
    var a=document.createElement('a');a.href=%(wa)s;a.target='_blank';a.rel='noopener';a.textContent='WhatsApp';st.appendChild(a);
    st.appendChild(document.createTextNode(' · '));
    var b=document.createElement('a');b.href=mailto;b.textContent='E-Mail';st.appendChild(b);
    btn.disabled=false;btn.textContent=label;
    if(window.umami)umami.track('formular-fehler');
  }
  f.addEventListener('submit',function(e){
    e.preventDefault();
    var E=f.elements, n=E['name'].value.trim(), m=E['email'].value.trim(), msg=E['message'].value.trim();
    if(!n||!m||!E['email'].checkValidity()){st.className='form-status err';st.textContent=%(alert)s;(n?E['email']:E['name']).focus();return;}
    btn.disabled=true;btn.textContent=%(sending)s;st.className='form-status';st.textContent='';
    var tr=E['termin']?E['termin'].value:'';
    var data={name:n,email:m,message:msg,termin:tr,website:E['website'].value,lang:%(lang)s,page:location.pathname,ms:Date.now()-t0};
    var ctl=window.AbortController?new AbortController():null, tm=setTimeout(function(){if(ctl)ctl.abort();},15000);
    fetch(f.action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data),signal:ctl?ctl.signal:undefined})
      .then(function(r){clearTimeout(tm);return r.json().catch(function(){return {};}).then(function(j){if(!r.ok||!j.ok)throw 0;});})
      .then(function(){f.hidden=true;ok.hidden=false;ok.focus();if(window.umami)umami.track('formular-gesendet');})
      .catch(function(){clearTimeout(tm);fail(n,m,(tr?'Termin: '+tr+'\\n\\n':'')+msg);});
  });
})();
</script>
"""


CAL_JS = r"""<script>
(function(){
  var root=document.getElementById('kcal'), f=document.getElementById('kform'); if(!root||!f||!window.Intl) return;
  var L=%(cal)s, WEEK=%(slots)s;
  var grid=root.querySelector('.cal-grid'), mEl=root.querySelector('.cal-month'), pv=root.querySelector('.cal-prev'), nx=root.querySelector('.cal-next'), tEl=root.querySelector('.cal-times');
  var hid=f.elements['termin'], chip=document.getElementById('kform-termin'), chipV=chip.querySelector('.ft-val'), btn=f.querySelector('.form-submit'), btnLabel=btn.textContent;
  function pad(n){return (n<10?'0':'')+n;}
  function key(d){return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());}
  function easter(y){var a=y%%19,b=Math.floor(y/100),c=y%%100,d=Math.floor(b/4),e=b%%4,f2=Math.floor((b+8)/25),g=Math.floor((b-f2+1)/3),h=(19*a+b-d-g+15)%%30,i=Math.floor(c/4),k=c%%4,l=(32+2*e+2*i-h-k)%%7,m=Math.floor((a+11*h+22*l)/451),mo=Math.floor((h+l-7*m+114)/31),da=((h+l-7*m+114)%%31)+1;return new Date(y,mo-1,da);}
  var H={};
  function hol(d){var y=d.getFullYear();if(!H[y]){var o={},e=easter(y);['01-01','05-01','10-03','11-01','12-24','12-25','12-26','12-31'].forEach(function(s){o[y+'-'+s]=1;});[-2,1,39,50,60].forEach(function(n){var x=new Date(e);x.setDate(x.getDate()+n);o[key(x)]=1;});H[y]=o;}return H[y][key(d)];}
  var now=new Date(), today=new Date(now.getFullYear(),now.getMonth(),now.getDate()), month0=new Date(today.getFullYear(),today.getMonth(),1);
  var S={}, first, last, cur, sel='';
  // termine.csv: Datum (16.11.2026 oder 2026-11-16) , Uhrzeit (12:00; mehrere: «10:00 15:00») , Notiz
  function parse(txt){
    var out={},n=0;
    txt.split(/\r?\n/).forEach(function(line){
      var c=line.split(/[;,\t]/); if(c.length<2)return;
      var ds=c[0].trim(), m, d;
      if((m=/^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(ds)))d=new Date(+m[1],m[2]-1,+m[3]);
      else if((m=/^(\d{1,2})\.(\d{1,2})\.(\d{4})$/.exec(ds)))d=new Date(+m[3],m[2]-1,+m[1]);
      else return;
      if(d<=today)return;
      var t=(c[1].match(/\d{1,2}:\d{2}/g)||[]).map(function(x){return x.length<5?'0'+x:x;}).sort();
      if(!t.length)return;
      out[key(d)]=t;n++;
    });
    return n?out:null;
  }
  function weekly(){var o={};for(var d=new Date(today.getFullYear(),today.getMonth(),today.getDate()+1),end=new Date(month0.getFullYear(),month0.getMonth()+2,1);d<end;d.setDate(d.getDate()+1)){if(WEEK[d.getDay()]&&!hol(d))o[key(d)]=[WEEK[d.getDay()]];}return o;}
  function init(map){
    S=map; var ks=Object.keys(S).sort();
    first=new Date(month0); last=new Date(month0.getFullYear(),month0.getMonth()+1,1);
    if(ks.length){var a=ks[0].split('-'),z=ks[ks.length-1].split('-');first=new Date(+a[0],a[1]-1,1);last=new Date(+z[0],z[1]-1,1);}
    var max=new Date(month0.getFullYear(),month0.getMonth()+3,1); if(last>max)last=max; if(first>last)first=new Date(last);
    cur=new Date(first); root.hidden=false; draw();
  }
  function day(k){var a=k.split('-');return new Date(+a[0],a[1]-1,+a[2]);}
  function nice(d,t){return new Intl.DateTimeFormat(L.loc,{weekday:'short',day:'numeric',month:'long'}).format(d)+', '+t;}
  function draw(){
    mEl.textContent=new Intl.DateTimeFormat(L.loc,{month:'long',year:'numeric'}).format(cur);
    pv.disabled=cur<=first; nx.disabled=cur>=last;
    grid.innerHTML=''; tEl.hidden=true; tEl.innerHTML='';
    L.wd.forEach(function(w){var s=document.createElement('span');s.className='cal-wd';s.textContent=w;grid.appendChild(s);});
    for(var i=(cur.getDay()+6)%%7;i>0;i--)grid.appendChild(document.createElement('span'));
    for(var d=new Date(cur);d.getMonth()===cur.getMonth();d.setDate(d.getDate()+1)){
      var k=key(d), ts=S[k], el;
      if(ts){
        var on=sel.slice(0,10)===k;
        el=document.createElement('button');el.type='button';el.className='cal-d free'+(on?' sel':'');
        el.setAttribute('aria-pressed',on?'true':'false');el.setAttribute('aria-label',nice(d,ts.join(', ')));
        el.innerHTML=d.getDate()+'<small>'+(ts.length>1?ts[0]+' +'+(ts.length-1):ts[0])+'</small>';
        el.addEventListener('click',open.bind(null,k));
      }else{el=document.createElement('span');el.className='cal-d';el.setAttribute('aria-hidden','true');el.textContent=d.getDate();}
      if(k===key(today))el.className+=' today';
      grid.appendChild(el);
    }
  }
  function open(k){
    var ts=S[k]; if(ts.length===1)return pick(k,ts[0]);
    draw(); tEl.innerHTML=''; var lb=document.createElement('span');lb.textContent=nice(day(k),'').replace(/, $/,'')+':';tEl.appendChild(lb);
    ts.forEach(function(t){var b=document.createElement('button');b.type='button';b.className='cal-t'+(sel===k+' '+t?' sel':'');b.textContent=t;b.addEventListener('click',function(){pick(k,t);});tEl.appendChild(b);});
    tEl.hidden=false; tEl.querySelector('button').focus();
  }
  function pick(k,t){
    sel=k+' '+t;hid.value=sel;chipV.textContent=nice(day(k),t);chip.hidden=false;btn.textContent=L.btn;draw();
    if(window.umami)umami.track('termin-gewaehlt');
    if(window.innerWidth<900)f.scrollIntoView({behavior:'smooth',block:'start'});
    var n=f.elements['name'];if(!n.value)setTimeout(function(){n.focus({preventScroll:true});},window.innerWidth<900?450:0);
  }
  chip.querySelector('button').addEventListener('click',function(){sel='';hid.value='';chip.hidden=true;btn.textContent=btnLabel;draw();});
  pv.addEventListener('click',function(){cur=new Date(cur.getFullYear(),cur.getMonth()-1,1);draw();});
  nx.addEventListener('click',function(){cur=new Date(cur.getFullYear(),cur.getMonth()+1,1);draw();});
  // Termine aus /termine.csv (auf GitHub bearbeitbar); fehlt die Datei oder steht nichts Zukünftiges drin → Wochenraster
  var done=false; function go(m){if(done)return;done=true;init(m||weekly());}
  setTimeout(function(){go(null);},4000);
  if(!window.fetch||location.protocol==='file:')return go(null);
  fetch('/termine.csv',{cache:'no-store'}).then(function(r){if(!r.ok)throw 0;return r.text();}).then(function(t){go(parse(t));}).catch(function(){go(null);});
})();
</script>
"""


def render(lang):
    t = T[lang]
    url = SITE + PATHS[lang]
    from urllib.parse import quote
    wa = "https://wa.me/%s?text=%s" % (WA_NUM, quote(t["wa_text"]))
    out = []
    w = out.append
    w('<!DOCTYPE html>\n<html lang="%s">\n<head>\n<meta charset="UTF-8">\n' % lang)
    w('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
    w('<title>%s</title>\n<meta name="description" content="%s">\n' % (esc(t["title"]), esc(t["desc"])))
    w('<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n' % (esc(t["og_title"]), esc(t["desc"])))
    w('<meta property="og:url" content="%s">\n<meta property="og:image" content="%simages/olha-portrait.jpg">\n' % (url, SITE))
    w('<meta property="og:type" content="website">\n<meta property="og:locale" content="%s">\n' % LOCALE[lang])
    w('<link rel="canonical" href="%s">\n' % url)
    for l2 in ("de", "uk", "ru"):
        w('<link rel="alternate" hreflang="%s" href="%s%s">\n' % (l2, SITE, PATHS[l2]))
    w('<link rel="alternate" hreflang="x-default" href="%s">\n' % SITE)
    w(jsonld(lang, t))
    w('<link rel="preload" href="/fonts/dm-serif-display-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>\n')
    w('<style>\n/* Schriften lokal gehostet (keine Verbindung zu Google Fonts) */\n' + FONTS + CSS + PZ_CSS + '</style>\n' + analytics_html() + '</head>\n<body>\n\n')

    # header
    w(header_html(lang))

    w('<main id="inhalt" tabindex="-1">\n\n')
    # hero
    w('<section class="hero" id="top">\n  <div class="wrap hero-inner">\n    <div class="hero-text">\n')
    w('      <div class="hero-eyebrow">%s</div>\n      <h1>%s</h1>\n      <p class="hero-claim">%s</p>\n      <p class="hero-sub">%s</p>\n' % (esc(t["eyebrow"]), esc(t["h1"]), t["claim"], esc(t["sub"])))
    w('      <div class="hero-btns">\n        <a href="#contact" class="btn-primary" data-umami-event="hero-cta">%s</a>\n        <a href="#pakete" class="btn-outline">%s</a>\n      </div>\n    </div>\n' % (esc(t["btn1"]), esc(t["btn2"])))
    w('    <div class="hero-photo">\n      <div class="hero-photo-frame">%s</div>\n' % pic("/images/olha-portrait.jpg", 900, 1350, t["photo_alt"], (480, 900), "(min-width:1200px) 460px, 40vw", 'fetchpriority="high" decoding="async"', hide_below=900))
    w('      <div class="hero-badge"><div class="hero-badge-num">%s</div><div class="hero-badge-lbl">%s</div></div>\n    </div>\n  </div>\n</section>\n\n' % (esc(t["badge_num"]), esc(t["badge_lbl"])))

    # metrics
    w('<div class="metrics">\n  <div class="wrap metrics-inner">\n')
    for num, lbl in t["metrics"]:
        w('    <div class="metric"><div class="metric-num">%s</div><div class="metric-lbl">%s</div></div>\n' % (esc(num), esc(lbl)))
    w('  </div>\n</div>\n\n')

    # why
    w('<section class="why">\n  <div class="wrap">\n    <div class="sec-label">%s</div>\n    <h2 class="sec-title">%s</h2>\n    <div class="why-grid">\n' % (esc(t["why_label"]), esc(t["why_title"])))
    for ic, h, p in t["why"]:
        w('      <div class="svc"><div class="svc-icon">%s</div><h3>%s</h3><p>%s</p></div>\n' % (ICON[ic], esc(h), esc(p)))
    w('    </div>\n  </div>\n</section>\n\n')

    # packages
    w('<section class="pakete" id="pakete">\n  <div class="wrap">\n    <div class="sec-label">%s</div>\n    <h2 class="sec-title">%s</h2>\n    <div class="pkg-grid">\n' % (esc(t["pk_label"]), esc(t["pk_title"])))
    for p in t["pk"]:
        w('      <article class="pkg%s">\n' % (" feat" if p.get("feat") else ""))
        w('        <div class="pkg-tag">%s</div>\n        <h3>%s</h3>\n        <div class="pkg-price">%s</div>\n' % (esc(p["tag"]), esc(p["name"]), p["price"]))
        w('        <div class="pkg-start">%s</div>\n        <p class="pkg-desc">%s</p>\n        <ul>\n' % (p["start"], esc(p["desc"])))
        for it in p["items"]:
            w('          <li>%s</li>\n' % esc(it))
        w('        </ul>\n        <p class="pkg-term">%s</p>\n        <a href="#contact" class="pkg-btn" data-umami-event="paket-anfragen" data-umami-event-paket="%s">%s</a>\n      </article>\n' % (esc(p["term"]), esc(_plain(p["name"])[:1]), esc(t["pk_btn"])))
    w('    </div>\n    <div class="pkg-extras">\n      <div class="pkg-extra">%s</div>\n      <div class="pkg-extra">%s</div>\n    </div>\n' % (t["pk_combo"], t["pk_addon"]))
    w('    <p class="pkg-note">%s</p>\n  </div>\n</section>\n\n' % esc(t["pk_note"]))

    # steps
    w('<section class="ablauf" id="ablauf">\n  <div class="wrap">\n    <div class="sec-label">%s</div>\n    <h2 class="sec-title">%s</h2>\n    <ol class="steps" style="list-style:none">\n' % (esc(t["st_label"]), esc(t["st_title"])))
    for i, (h, p) in enumerate(t["steps"], 1):
        w('      <li class="step"><div class="step-num" aria-hidden="true">%d</div><h3>%s</h3><p>%s</p></li>\n' % (i, esc(h), esc(p)))
    w('    </ol>\n  </div>\n</section>\n\n')

    # cases
    w('<section class="cases" id="ergebnisse">\n  <div class="wrap">\n    <div class="sec-label">%s</div>\n    <h2 class="sec-title">%s</h2>\n    <div class="cases-grid">\n' % (esc(t["cs_label"]), esc(t["cs_title"])))
    def case_html(c):
        name = esc(c["name"])
        if c.get("link"):
            name = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (c["link"], name)
        cls = (" wide" if c.get("wide") else "") + (" has-img" if c.get("img") else "")
        w('      <div class="case%s">\n' % cls)
        if c.get("img"):
            w('        <a class="case-img" href="%s" target="_blank" rel="noopener">%s</a>\n        <div>\n' % (c["link"], pic(c["img"], 1200, 750, c["img_alt"], (600, 1200), "(max-width:900px) 92vw, 560px")))
        w('        <div class="case-tag">%s</div>\n        <h3>%s</h3>\n        <p>%s</p>\n' % (esc(c["tag"]), name, esc(c["text"])))
        if c.get("quote"):
            w('        <blockquote class="case-quote" lang="%s">„%s“<cite lang="%s">%s</cite></blockquote>\n' % (c.get("quote_lang", "de"), esc(c["quote"]), lang, esc(c["cite"])))
        w('        <div class="case-result">')
        for num, lbl in c["res"]:
            w('<div class="result-item"><div class="r-num">%s</div><div class="r-lbl">%s</div></div>' % (esc(num), esc(lbl)))
        w('</div>\n' + ('        </div>\n' if c.get("img") else '') + '      </div>\n')
    for c in t["cases"]:
        case_html(c)
    if t.get("demos"):
        w('    </div>\n    <div class="demo-head"><h3>%s</h3><p>%s</p></div>\n    <div class="cases-grid">\n' % (esc(t["dm_title"]), esc(t["dm_sub"])))
        for c in t["demos"]:
            case_html(c)
    w('    </div>\n    <p class="also">%s</p>\n  </div>\n</section>\n\n' % t["also"])

    # about
    w('<section class="about" id="about">\n  <div class="wrap about-grid">\n    <div class="about-img">\n')
    w('      <div class="about-img-frame">%s</div>\n' % pic("/images/olha-arbeit.jpg", 1100, 734, t["ab_img_alt"], (550, 1100), "(max-width:900px) 92vw, 520px"))
    w('      <div class="about-card"><div class="about-card-title">%s</div><div class="about-card-langs">' % esc(t["ab_langs"]))
    for color, nm, l2 in (("#005BBB", "Українська", "uk"), ("#CC0000", "Русский", "ru")):
        w('<div class="lang-row" lang="%s"><span class="lang-dot" style="background:%s"></span>%s</div>' % (l2, color, nm))
    w('</div></div>\n    </div>\n    <div class="about-text">\n      <div class="sec-label">%s</div>\n      <h2>%s</h2>\n' % (esc(t["ab_label"]), esc(t["ab_title"])))
    for p in t["ab"]:
        w('      <p>%s</p>\n' % esc(p))
    w('      <div class="about-skills">')
    for s in ("Google Maps", "Google SEO", "Search Console", "Shopify", "Instagram", "Telegram", "Pinterest", "Canva", "Analytics", "Copywriting"):
        w('<span class="skill">%s</span>' % s)
    w('</div>\n    </div>\n  </div>\n')
    w(puzzle_html(lang, t))
    w('</section>\n\n')

    # faq
    w('<section class="faq" id="faq">\n  <div class="wrap">\n    <div class="sec-label">%s</div>\n    <h2 class="sec-title">%s</h2>\n    <div class="faq-list">\n' % (esc(t["fq_label"]), esc(t["fq_title"])))
    for f in t["faq"]:
        q, a = f[0], f[1]
        more = ' <a class="inl" href="%s">%s</a>' % (f[2], esc(f[3])) if len(f) > 2 else ""
        w('      <details><summary>%s</summary><p>%s%s</p></details>\n' % (esc(q), esc(a), more))
    w('    </div>\n  </div>\n</section>\n\n')

    # contact
    w('<section class="contact" id="contact">\n  <div class="wrap contact-inner">\n    <div>\n')
    w('      <h2>%s</h2>\n      <p class="contact-sub">%s</p>\n      <div class="contact-methods">\n' % (t["ct_title"], esc(t["ct_sub"])))
    w('        <a class="cm wa" href="%s" target="_blank" rel="noopener" data-umami-event="kontakt-whatsapp" title="%s" aria-label="%s"><span class="cm-ic">%s</span></a>\n' % (esc(wa), esc(t["wa_label"]), esc(t["wa_label"]), ICON["wa"]))
    w('        <a class="cm" href="mailto:%s?subject=%%5BWebsite%%5D%%20Google-Check" data-umami-event="kontakt-email" title="E-Mail" aria-label="E-Mail"><span class="cm-ic">%s</span></a>\n' % (EMAIL, ICON["mail"]))
    w('        <a class="cm" href="%s" target="_blank" rel="noopener" data-umami-event="kontakt-linkedin" title="LinkedIn" aria-label="LinkedIn"><span class="cm-ic">%s</span></a>\n' % (LINKEDIN, ICON["in"]))
    if GBP_URL:
        w('        <a class="cm" href="%s" target="_blank" rel="noopener" data-umami-event="kontakt-google-profil" title="Google-Profil" aria-label="Google-Profil"><span class="cm-ic">%s</span></a>\n' % (GBP_URL, ICON["g"]))
    w('      </div>\n')
    cu = CAL_UI[lang]
    w('      <div class="cal" id="kcal" hidden>\n        <h3>%s</h3>\n        <p class="cal-sub">%s</p>\n' % (esc(cu["title"]), esc(cu["sub"])))
    w('        <div class="cal-head"><button type="button" class="cal-nav cal-prev" aria-label="%s">&#8249;</button><div class="cal-month" aria-live="polite"></div><button type="button" class="cal-nav cal-next" aria-label="%s">&#8250;</button></div>\n' % (esc(cu["prev"]), esc(cu["next"])))
    w('        <div class="cal-grid"></div>\n        <div class="cal-times" hidden></div>\n        <div class="cal-legend"><span><i class="lf"></i>%s</span><span><i class="ln"></i>%s</span></div>\n      </div>\n' % (esc(cu["free"]), esc(cu["none"])))
    w('    </div>\n')
    fu = FORM_UI[lang]
    w('    <form class="contact-form" id="kform" action="%s" method="post" novalidate>\n      <h3>%s</h3>\n' % (FORM_ENDPOINT, esc(t["f_title"])))
    w('      <div class="form-row"><label for="f-name">%s</label><input id="f-name" name="name" type="text" autocomplete="name" required maxlength="100" placeholder="%s"></div>\n' % (esc(t["f_name"]), esc(t["f_ph_name"])))
    w('      <div class="form-row"><label for="f-mail">%s</label><input id="f-mail" name="email" type="email" autocomplete="email" required maxlength="200" placeholder="name@email.de"></div>\n' % esc(t["f_mail"]))
    w('      <div class="form-row"><label for="f-msg">%s</label><textarea id="f-msg" name="message" maxlength="3000" placeholder="%s"></textarea></div>\n' % (esc(t["f_msg"]), esc(t["f_ph_msg"])))
    w('      <input type="hidden" name="termin" value="">\n')
    w('      <div class="form-termin" id="kform-termin" hidden><span><b>%s</b> <span class="ft-val"></span><em>%s</em></span><button type="button" aria-label="%s">&times;</button></div>\n' % (esc(cu["chip"]), esc(cu["note"]), esc(cu["remove"])))
    # ловушка для ботов: человек это поле не видит и не заполняет
    w('      <div class="hp" aria-hidden="true"><label for="f-web">Website</label><input id="f-web" name="website" type="text" tabindex="-1" autocomplete="off"></div>\n')
    w('      <button type="submit" class="form-submit">%s</button>\n      <p class="form-note">%s <a href="/datenschutz.html">Datenschutz</a></p>\n' % (esc(t["f_btn"]), esc(t["f_note"])))
    w('      <div class="form-status" id="kform-status" role="status" aria-live="polite"></div>\n    </form>\n')
    w('    <div class="form-ok" id="kform-ok" tabindex="-1" hidden><div class="form-ok-ic" aria-hidden="true">✓</div><h3>%s</h3><p>%s</p></div>\n  </div>\n</section>\n\n' % (esc(fu["ok_t"]), esc(fu["ok"])))

    w('</main>\n\n')
    # footer
    w(footer_html())

    # script
    w(FORM_JS % dict(alert=json.dumps(t["f_alert"], ensure_ascii=False), lang=json.dumps(lang),
                     sending=json.dumps(fu["sending"], ensure_ascii=False), err=json.dumps(fu["err"], ensure_ascii=False),
                     wa=json.dumps(wa), mail=json.dumps(EMAIL), label=json.dumps(LABELS[lang])))
    cu = CAL_UI[lang]
    w(CAL_JS % dict(cal=json.dumps(dict(loc=cu["loc"], wd=cu["wd"], btn=cu["btn"]), ensure_ascii=False),
                    slots=json.dumps({str(k): v for k, v in CAL_SLOTS.items()})))
    w(wa_float(lang) + BURGER_JS + '</body>\n</html>\n')
    # неразрывный пробел перед €, чтобы цена не разрывалась
    return "".join(out).replace(" €", "\u00a0€")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    for lang in ("de", "uk", "ru"):
        d = os.path.join(root, PATHS[lang])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render(lang))
        print("ok", lang, os.path.join(d, "index.html"))


if __name__ == "__main__":
    main()
