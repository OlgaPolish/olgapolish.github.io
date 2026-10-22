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
.hero h1{font-family:'DM Serif Display',serif;font-weight:400;font-size:clamp(2.3rem,4.4vw,3.5rem);line-height:1.1;letter-spacing:-0.02em;margin-bottom:20px;color:var(--ink)}
.hero h1 em{font-style:italic;color:var(--amber)}
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
.form-note{font-size:12px;color:rgba(255,255,255,0.55);margin-top:12px;line-height:1.5}
.form-note a{color:rgba(255,255,255,0.8);text-decoration:underline}

/* FOOTER */
footer{background:#111827;padding:32px 0}
.foot-inner{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}
.foot-copy{font-size:13px;color:rgba(255,255,255,0.5)}
.foot-links{display:flex;gap:20px;flex-wrap:wrap}
.foot-links a{font-size:13px;color:rgba(255,255,255,0.5);transition:color .2s}
.foot-links a:hover{color:rgba(255,255,255,0.85)}

@media(max-width:980px){.nav-links{display:none}}
@media(max-width:900px){
  .hero-inner,.about-grid,.contact-inner{grid-template-columns:1fr;gap:40px}
  .hero-photo{display:none}
  .why-grid{grid-template-columns:1fr 1fr}
  .pkg-grid,.pkg-extras,.cases-grid{grid-template-columns:1fr}
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
    "in": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z"/><circle cx="4" cy="4" r="2"/></svg>',
}

# ---------------------------------------------------------------- ТЕКСТЫ
T = {}

T["de"] = dict(
    title="Olha Polishchuk — Google-Profil, Webseite & SEO in Düsseldorf",
    desc="Damit Kunden Sie in Google finden: Google-Unternehmensprofil, Onepager-Webseite und Betreuung für kleine Unternehmen in Düsseldorf und ganz Deutschland. Auf Deutsch, Ukrainisch und Russisch.",
    og_title="Olha Polishchuk — Google-Profil, Webseite & SEO · Düsseldorf",
    nav=["Pakete", "Ablauf", "Ergebnisse", "Über mich", "Kontakt"],
    cta_nav="Kostenloser Google-Check",
    eyebrow="Düsseldorf · NRW · deutschlandweit remote",
    h1="Ihre Kunden suchen Sie in Google. Ich sorge dafür, dass sie Sie <em>finden</em>.",
    sub="Google-Unternehmensprofil, Onepager-Webseite und laufende Betreuung für kleine Unternehmen in Deutschland. Wir sprechen Deutsch, Ukrainisch oder Russisch — die Texte für Ihre Kunden schreibe ich auf Deutsch, klar und korrekt.",
    btn1="Kostenloser Google-Check →", btn2="Pakete & Preise",
    photo_alt="Olha Polishchuk — Google-Profil, Webseiten und SEO in Düsseldorf",
    badge_num="Nr. 1", badge_lbl="in Google für einen Kunden",
    metrics=[("3 Sprachen", "Deutsch · Ukrainisch · Russisch"), ("Google SEO", "praktische Erfahrung"), ("Ganz Deutschland", "remote und in Düsseldorf")],
    why_label="Warum mit mir", why_title="Einfach, verständlich — in Ihrer Sprache",
    why=[("chat", "Wir sprechen dieselbe Sprache", "Sie erklären auf Deutsch, Ukrainisch oder Russisch, ich schreibe für Ihre Kunden auf Deutsch. Ohne Dolmetscher, ohne Missverständnisse."),
         ("hand", "Ich mache das für Sie", "Sie schicken Fotos und ein paar Sätze zu Ihrer Arbeit — den Rest übernehme ich. Sie prüfen nur und sagen „Ja“."),
         ("doc", "Alles schriftlich", "Preis, Umfang und Termine stehen vorab im Angebot. Keine Überraschungen auf der Rechnung."),
         ("chart", "In der Praxis erprobt", "Was ich Kunden anbiete, teste ich zuerst in eigenen Projekten — und sehe das Ergebnis in Zahlen.")],
    pk_label="Pakete & Preise", pk_title="Klare Preise — ohne Überraschungen", pk_btn="Anfragen",
    pk=[dict(tag="Einmalig", name="A · „Man findet Sie in Google“", price="190 €",
             start="<strong>Startpreis für die ersten 3 Kunden: 150 €</strong> — gegen eine kurze schriftliche Bewertung",
             desc="Ihr Unternehmensprofil in Google Maps — neu eingerichtet oder aufgeräumt:",
             items=["passende Kategorien und Leistungen, Beschreibung auf Deutsch (und Ukrainisch / Russisch)",
                    "Fotos, Öffnungszeiten, Kontakt, Link zu WhatsApp oder Webseite",
                    "die ersten 3 Beiträge im Profil",
                    "QR-Code und fertige Nachricht, um Kundenbewertungen zu sammeln",
                    "falls Sie eine Webseite haben: Titel und Beschreibungen der wichtigsten Seiten, Einrichtung der Google Search Console"],
             term="Dauer: ca. 1 Woche."),
        dict(tag="Einmalig", name="B · Onepager-Webseite", price="450 €",
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
        dict(tag="Monatlich", name="C · Betreuung", price="290 € <small>/ Monat</small>", feat=True,
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
    cases=[dict(wide=True, tag="SEO · Shopify · Düsseldorf", name="Kanelia — Shop für Nageldesign-Bedarf", link="https://kaneliastore.com/",
                text="SEO-Überarbeitung des Shopify-Shops: Produktseiten, Seitenstruktur, lokale Sichtbarkeit. Ergebnisse nach 2–3 Monaten — laut Google Search Console und Shopify.",
                res=[("Nr. 1", "in Google für „nagelsticker kaufen“"), ("4–5 → 65", "Besuche aus Google pro Monat"), ("9 von 11", "ersten Online-Bestellungen kamen über Google")]),
           dict(tag="Onepager · in Abstimmung", name="Webseite für ein Ingenieurbüro aus Charkiw (АВ-Концепція)",
                text="Onepager mit Portfolio auf Ukrainisch — erstellt aus PDFs, alten .doc-Dateien und über 80 Fotos des Kunden. Der Kunde musste nur noch prüfen.",
                res=[("51", "Objekte mit Filter und Suche"), ("279 → 8 MB", "Bilder komprimiert — schnell auf dem Smartphone")]),
           dict(tag="Eigenes Projekt · Webseite · Pinterest", name="EaseMyFeed — mein eigenes Projekt", link="https://easemyfeed.com/",
                text="Webseite mit 13 Seiten und eigener Domain, Search Console, Pinterest und Instagram — alles selbst umgesetzt. Hier teste ich zuerst, was ich später für Kunden mache.",
                res=[("7.057", "Pinterest-Impressionen in 30 Tagen"), ("+61 %", "zum Vormonat")]),
           dict(tag="Content · SMM", name="FinanzGuide GE — Content für eine Finanzberaterin in Düsseldorf",
                text="Markenstimme, visuelles System und regelmäßige Beiträge für russisch- und ukrainischsprachige Familien in NRW.",
                res=[("39.933", "Aufrufe des besten Beitrags")])],
    also="<strong>Außerdem:</strong> Betreuung von Instagram und Telegram, Einrichtung und Optimierung von Shopify-Shops, Texte auf Deutsch, Ukrainisch und Russisch. Schreiben Sie mir — wir besprechen es.",
    ab_label="Über mich", ab_title="Hallo, ich bin Olha", ab_img_alt="Olha Polishchuk am Laptop",
    ab_langs="Sprachen",
    ab=["Ich lebe in Düsseldorf. Mein Hintergrund sind Programmierung und Datenanalyse — deshalb achte ich nicht nur darauf, dass es gut aussieht, sondern auch auf die Zahlen: wie viele Menschen Sie gefunden haben und was sie danach getan haben.",
        "Ich spreche Deutsch, Ukrainisch, Russisch und Englisch und arbeite mit kleinen Unternehmen: Nagel- und Kosmetikstudios, Friseuren, Cafés, Läden, Handwerk und Dienstleistern."],
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
    f_note="Beim Absenden öffnet sich Ihr E-Mail-Programm. Es werden keine Daten auf dieser Website gespeichert.",
    f_alert="Bitte Name und E-Mail ausfüllen.", lang_name="Sprache",
)

T["uk"] = dict(
    title="Ольга Поліщук — Google-профіль, сайт-візитка та SEO в Дюссельдорфі",
    desc="Щоб клієнти знаходили вас у Google: профіль у Google Maps, сайт-візитка та підтримка для україно- та російськомовного бізнесу в Німеччині. Düsseldorf і вся Німеччина.",
    og_title="Ольга Поліщук — Google-профіль, сайт і SEO · Düsseldorf",
    nav=["Пакети", "Як працюємо", "Результати", "Про мене", "Контакт"],
    cta_nav="Безкоштовний аудит",
    eyebrow="Düsseldorf · NRW · дистанційно по всій Німеччині",
    h1="Клієнти шукають вас у Google. Зроблю так, щоб вони вас <em>знайшли</em>.",
    sub="Допомагаю україно- та російськомовному малому бізнесу в Німеччині: профіль у Google Maps, сайт-візитка та регулярна підтримка. Спілкуємося українською або російською — тексти для ваших клієнтів пишу грамотною німецькою.",
    btn1="Отримати безкоштовний аудит у Google →", btn2="Пакети та ціни",
    photo_alt="Ольга Поліщук — Google-профіль, сайти та SEO в Дюссельдорфі",
    badge_num="№ 1", badge_lbl="у Google для клієнта",
    metrics=[("3 мови", "спілкування: DE · UA · RU"), ("Google SEO", "практичний досвід"), ("Уся Німеччина", "дистанційно та в Düsseldorf")],
    why_label="Чому зі мною зручно", why_title="Просто, зрозуміло й вашою мовою",
    why=[("chat", "Говоримо однією мовою", "Ви пояснюєте українською чи російською, я пишу для ваших клієнтів німецькою. Без перекладача й без непорозумінь."),
         ("hand", "Роблю за вас", "Ви надсилаєте фото й кілька слів про свою роботу — решта на мені. Від вас потрібно лише перевірити й сказати «так»."),
         ("doc", "Усе письмово", "Ціна, обсяг і терміни — заздалегідь у пропозиції. Жодних сюрпризів у рахунку."),
         ("chart", "Перевірено на практиці", "Те, що пропоную клієнтам, спершу роблю для власних проєктів і бачу результат у цифрах.")],
    pk_label="Пакети та ціни", pk_title="Зрозумілі ціни — без сюрпризів", pk_btn="Обговорити",
    pk=[dict(tag="Разово", name="A · «Вас знаходять у Google»", price="190 €",
             start="<strong>Стартова ціна для перших 3 клієнтів: 150 €</strong> — в обмін на короткий письмовий відгук",
             desc="Профіль вашої компанії в Google Maps — створю з нуля або наведу лад:",
             items=["правильні категорії та послуги, опис німецькою (і українською / російською)",
                    "фото, години роботи, контакти, посилання на WhatsApp або сайт",
                    "3 перші публікації в профілі",
                    "QR-код і готове повідомлення, щоб збирати відгуки клієнтів",
                    "якщо у вас є сайт — заголовки й описи головних сторінок, підключення Google Search Console"],
             term="Термін: близько 1 тижня."),
        dict(tag="Разово", name="B · Сайт-візитка", price="450 €",
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
        dict(tag="Щомісяця", name="C · Підтримка", price="290 € <small>/ міс</small>", feat=True,
             start="<strong>Перший місяць для перших 3 клієнтів: 220 €</strong>",
             desc="Щоб вас не просто знайшли один раз, а знаходили постійно:",
             items=["4 публікації на місяць у профілі Google",
                    "відповіді на відгуки (надсилаю чернетку, ви погоджуєте)",
                    "оновлення фото, годин роботи, акцій",
                    "дрібні правки сайту",
                    "щомісяця покращую для Google одну сторінку або послугу",
                    "короткий звіт раз на місяць: скільки людей вас знайшли, зателефонували, проклали маршрут"],
             term="Мінімум 3 місяці — перші результати в Google зазвичай видно через 2–3 місяці.")],
    pk_combo="<strong>A + B разом — 590 €</strong> замість 640 €. Google-профіль і сайт в одних руках.",
    pk_addon="<strong>Додатково до підтримки: контент за вас — +190 € на місяць.</strong> 12 дописів на місяць для Instagram, Telegram або Threads: тексти, прості картинки, публікація за розкладом.",
    pk_note="Ціни остаточні: як Kleinunternehmer за § 19 UStG я не нараховую ПДВ. Точний обсяг робіт фіксуємо письмово в пропозиції.",
    st_label="Як ми працюємо", st_title="Чотири кроки — і вас видно",
    steps=[("Безкоштовний аудит", "Ви пишете, чим займаєтеся і в якому місті. Я дивлюся, як вас зараз видно в Google, і надсилаю короткий чек-лист точок зростання: що вже добре, що заважає і що можна покращити."),
           ("Пропозиція", "Якщо хочете, щоб я зробила це за вас, — надсилаю пропозицію з ціною, обсягом і терміном."),
           ("Робота", "Ви надсилаєте фото й інформацію, я роблю. Показую результат, вносимо правки."),
           ("Готово", "Рахунок — після виконання. Якщо потрібно — далі підтримка.")],
    cs_label="Результати", cs_title="Реальні результати для реального бізнесу",
    cases=[dict(wide=True, tag="SEO · Shopify · Düsseldorf", name="Kanelia — магазин матеріалів для манікюру", link="https://kaneliastore.com/",
                text="SEO-переробка Shopify-магазину: картки товарів, структура сайту, локальна видимість. Результати через 2–3 місяці — за даними Google Search Console і Shopify.",
                res=[("№ 1", "у Google за запитом «nagelsticker kaufen»"), ("4–5 → 65", "візитів із Google на місяць"), ("9 з 11", "перших онлайн-замовлень — із Google")]),
           dict(tag="Сайт-візитка · на погодженні", name="Сайт для інженерної компанії «АВ-Концепція» (Харків)",
                text="Сайт-візитка з портфоліо українською — зібраний із PDF, старих .doc-файлів і 80+ фото замовника. Клієнт лише перевіряв.",
                res=[("51", "об'єкт із фільтрами й пошуком"), ("279 → 8 МБ", "фото стиснуто — сайт швидко відкривається з телефона")]),
           dict(tag="Власний проєкт · Сайт · Pinterest", name="EaseMyFeed — мій власний проєкт", link="https://easemyfeed.com/",
                text="Сайт на 13 сторінок із власним доменом, Search Console, Pinterest та Instagram — усе зроблено самостійно. Тут я спершу перевіряю те, що потім роблю для клієнтів.",
                res=[("7 057", "показів у Pinterest за 30 днів"), ("+61 %", "до минулого місяця")]),
           dict(tag="Контент · SMM", name="FinanzGuide GE — контент для фінансової консультантки в Düsseldorf",
                text="Голос бренду, візуальна система та регулярні публікації для україно- та російськомовної аудиторії в NRW.",
                res=[("39 933", "перегляди найкращої публікації")])],
    also="<strong>Також можу допомогти:</strong> ведення Instagram і Telegram, налаштування й оптимізація Shopify-магазинів, тексти німецькою, українською та російською. Напишіть — обговоримо.",
    ab_label="Про мене", ab_title="Привіт, я Ольга", ab_img_alt="Ольга Поліщук за ноутбуком",
    ab_langs="Мови",
    ab=["Живу в Düsseldorf. За освітою й досвідом — програмування та аналіз даних, тому дивлюся не лише на «гарно», а й на цифри: скільки людей вас знайшли і що вони зробили далі.",
        "Говорю німецькою, українською, російською та англійською. Працюю з невеликими бізнесами: майстрами, салонами, кафе, магазинами, ремонтом і послугами."],
    fq_label="Часті запитання", fq_title="Відповіді на часті запитання",
    faq=[("У мене є Instagram. Навіщо ще Google?", "Коли людина шукає «манікюр поруч» або «Friseur Düsseldorf», вона відкриває Google і Google Maps, а не Instagram. Профіль у Google — це безкоштовна вивіска там, де вас шукають саме зараз."),
         ("Що мені потрібно для початку?", "Кілька фото вашої роботи, список послуг із цінами, адреса й години роботи. Якщо чогось немає — підкажу, як швидко це зробити."),
         ("Ви працюєте лише в Düsseldorf?", "Ні, дистанційно по всій Німеччині. Зустрітися особисто можу в Düsseldorf і поруч."),
         ("Як оплачувати?", "За рахунком (Rechnung) після виконання роботи. Без ПДВ — я Kleinunternehmer за § 19 UStG."),
         ("Чи можна спілкуватися лише письмово?", "Так, так навіть зручніше: усе залишається в листуванні, і нічого не забувається.")],
    ct_title="Отримайте безкоштовний <em>аудит</em> у Google",
    ct_sub="Напишіть, чим ви займаєтеся і в якому місті. Я подивлюся ваш профіль і сайт та надішлю короткий чек-лист точок зростання: що вже добре і що заважає клієнтам вас знайти. Безкоштовно й без зобов'язань. Відповідаю протягом 24 годин.",
    wa_label="WhatsApp", wa_text="Добрий день! Хочу безкоштовний аудит у Google.",
    f_title="Безкоштовний аудит", f_name="Ім'я", f_mail="E-Mail", f_msg="Чим ви займаєтеся і в якому місті?",
    f_ph_name="Ваше ім'я", f_ph_msg="Наприклад: манікюр, Düsseldorf-Benrath", f_btn="Отримати безкоштовний аудит →",
    f_note="Після натискання відкриється ваша поштова програма. Сайт не зберігає жодних даних.",
    f_alert="Будь ласка, заповніть ім'я та e-mail.", lang_name="Мова",
)

T["ru"] = dict(
    title="Ольга Полищук — Google-профиль, сайт-визитка и SEO в Дюссельдорфе",
    desc="Чтобы клиенты находили вас в Google: профиль в Google Maps, сайт-визитка и поддержка для русско- и украиноязычного бизнеса в Германии. Düsseldorf и вся Германия.",
    og_title="Ольга Полищук — Google-профиль, сайт и SEO · Düsseldorf",
    nav=["Пакеты", "Как работаем", "Результаты", "Обо мне", "Контакт"],
    cta_nav="Бесплатный аудит",
    eyebrow="Düsseldorf · NRW · по всей Германии удалённо",
    h1="Клиенты ищут вас в Google. Сделаю так, чтобы они вас <em>нашли</em>.",
    sub="Помогаю русско- и украиноязычному малому бизнесу в Германии: профиль в Google Maps, сайт-визитка и регулярная поддержка. Общаемся по-русски или по-украински — тексты для ваших клиентов пишу на грамотном немецком.",
    btn1="Получить бесплатный аудит в Google →", btn2="Пакеты и цены",
    photo_alt="Ольга Полищук — Google-профиль, сайты и SEO в Дюссельдорфе",
    badge_num="№ 1", badge_lbl="в Google для клиента",
    metrics=[("3 языка", "общения: DE · UA · RU"), ("Google SEO", "практический опыт"), ("Вся Германия", "удалённо и в Düsseldorf")],
    why_label="Почему со мной удобно", why_title="Просто, понятно и на вашем языке",
    why=[("chat", "Говорим на одном языке", "Вы объясняете по-русски или по-украински, я пишу для ваших клиентов по-немецки. Без переводчика и без недопонимания."),
         ("hand", "Делаю за вас", "Вы присылаете фото и пару слов о своей работе — остальное на мне. От вас нужно только проверить и сказать «да»."),
         ("doc", "Всё письменно", "Цена, объём и сроки — заранее в предложении. Никаких сюрпризов в счёте."),
         ("chart", "Проверено на практике", "То, что предлагаю клиентам, сначала делаю для своих проектов и вижу результат в цифрах.")],
    pk_label="Пакеты и цены", pk_title="Понятные цены — без сюрпризов", pk_btn="Обсудить",
    pk=[dict(tag="Разово", name="A · «Вас находят в Google»", price="190 €",
             start="<strong>Стартовая цена для первых 3 клиентов: 150 €</strong> — в обмен на короткий письменный отзыв",
             desc="Профиль вашей компании в Google Maps — создам с нуля или приведу в порядок:",
             items=["правильные категории и услуги, описание на немецком (и на русском / украинском)",
                    "фото, часы работы, контакты, ссылка на WhatsApp или сайт",
                    "3 первые публикации в профиле",
                    "QR-код и готовое сообщение, чтобы собирать отзывы клиентов",
                    "если у вас есть сайт — заголовки и описания главных страниц, подключение Google Search Console"],
             term="Срок: около 1 недели."),
        dict(tag="Разово", name="B · Сайт-визитка", price="450 €",
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
        dict(tag="Каждый месяц", name="C · Поддержка", price="290 € <small>/ мес</small>", feat=True,
             start="<strong>Первый месяц для первых 3 клиентов: 220 €</strong>",
             desc="Чтобы вас не просто нашли один раз, а находили постоянно:",
             items=["4 публикации в месяц в профиле Google",
                    "ответы на отзывы (присылаю черновик, вы согласуете)",
                    "обновление фото, часов, акций",
                    "мелкие правки сайта",
                    "каждый месяц улучшаю для Google одну страницу или услугу",
                    "короткий отчёт раз в месяц: сколько людей вас нашли, позвонили, проложили маршрут"],
             term="Минимум 3 месяца — первые результаты в Google обычно видны через 2–3 месяца.")],
    pk_combo="<strong>A + B вместе — 590 €</strong> вместо 640 €. Google-профиль и сайт в одних руках.",
    pk_addon="<strong>Дополнительно к поддержке: контент за вас — +190 € в месяц.</strong> 12 постов в месяц для Instagram, Telegram или Threads: тексты, простые картинки, публикация по расписанию.",
    pk_note="Цены окончательные: как Kleinunternehmer по § 19 UStG я не начисляю НДС. Точный объём работ фиксируем письменно в предложении.",
    st_label="Как мы работаем", st_title="Четыре шага — и вас видно",
    steps=[("Бесплатный аудит", "Вы пишете, чем занимаетесь и в каком городе. Я смотрю, как вас сейчас видно в Google, и присылаю короткий чек-лист точек роста: что уже хорошо, что мешает и что можно улучшить."),
           ("Предложение", "Если хотите, чтобы я сделала это за вас, — присылаю предложение с ценой, объёмом и сроком."),
           ("Работа", "Вы присылаете фото и информацию, я делаю. Показываю результат, вносим правки."),
           ("Готово", "Счёт после выполнения. Если нужно — дальше поддержка.")],
    cs_label="Результаты", cs_title="Реальные результаты для реального бизнеса",
    cases=[dict(wide=True, tag="SEO · Shopify · Düsseldorf", name="Kanelia — магазин материалов для маникюра", link="https://kaneliastore.com/",
                text="SEO-переработка Shopify-магазина: карточки товаров, структура сайта, локальная видимость. Результаты через 2–3 месяца — по данным Google Search Console и Shopify.",
                res=[("№ 1", "в Google по запросу «nagelsticker kaufen»"), ("4–5 → 65", "визитов из Google в месяц"), ("9 из 11", "первых онлайн-заказов — из Google")]),
           dict(tag="Сайт-визитка · на согласовании", name="Сайт для инженерной компании «АВ-Концепція» (Харьков)",
                text="Сайт-визитка с портфолио на украинском — собран из PDF, старых .doc-файлов и 80+ фото заказчика. Клиент только проверял.",
                res=[("51", "объект с фильтрами и поиском"), ("279 → 8 МБ", "фото сжаты — сайт быстро открывается с телефона")]),
           dict(tag="Свой проект · Сайт · Pinterest", name="EaseMyFeed — мой собственный проект", link="https://easemyfeed.com/",
                text="Сайт на 13 страниц со своим доменом, Search Console, Pinterest и Instagram — всё сделано самостоятельно. Здесь я сначала проверяю то, что потом делаю для клиентов.",
                res=[("7 057", "показов в Pinterest за 30 дней"), ("+61 %", "к прошлому месяцу")]),
           dict(tag="Контент · SMM", name="FinanzGuide GE — контент для финансового консультанта в Düsseldorf",
                text="Голос бренда, визуальная система и регулярные публикации для русско- и украиноязычной аудитории в NRW.",
                res=[("39 933", "просмотра у лучшей публикации")])],
    also="<strong>Также могу помочь:</strong> ведение Instagram и Telegram, настройка и оптимизация Shopify-магазинов, тексты на немецком, русском и украинском. Напишите — обсудим.",
    ab_label="Обо мне", ab_title="Привет, я Ольга", ab_img_alt="Ольга Полищук за ноутбуком",
    ab_langs="Языки",
    ab=["Живу в Düsseldorf. По образованию и опыту — программирование и анализ данных, поэтому смотрю не только на «красиво», но и на цифры: сколько людей вас нашли и что они сделали дальше.",
        "Говорю на немецком, украинском, русском и английском. Работаю с небольшими бизнесами: мастерами, салонами, кафе, магазинами, ремонтом и услугами."],
    fq_label="Частые вопросы", fq_title="Ответы на частые вопросы",
    faq=[("У меня есть Instagram. Зачем ещё Google?", "Когда человек ищет «маникюр рядом» или «Friseur Düsseldorf», он открывает Google и Google Maps, а не Instagram. Профиль в Google — это бесплатная вывеска там, где вас ищут прямо сейчас."),
         ("Что мне нужно для начала?", "Пару фото вашей работы, список услуг с ценами, адрес и часы работы. Если чего-то нет — подскажу, как быстро сделать."),
         ("Вы работаете только в Düsseldorf?", "Нет, по всей Германии удалённо. Встретиться лично могу в Düsseldorf и рядом."),
         ("Как оплачивать?", "По счёту (Rechnung) после выполнения работы. Без НДС — я Kleinunternehmer по § 19 UStG."),
         ("Можно ли общаться только письменно?", "Да, так даже удобнее: всё остаётся в переписке, и ничего не забывается.")],
    ct_title="Получите бесплатный <em>аудит</em> в Google",
    ct_sub="Напишите, чем вы занимаетесь и в каком городе. Я посмотрю ваш профиль и сайт и пришлю короткий чек-лист точек роста: что уже хорошо и что мешает клиентам вас найти. Бесплатно и без обязательств. Отвечаю в течение 24 часов.",
    wa_label="WhatsApp", wa_text="Здравствуйте! Хочу бесплатный аудит в Google.",
    f_title="Бесплатный аудит", f_name="Имя", f_mail="E-Mail", f_msg="Чем вы занимаетесь и в каком городе?",
    f_ph_name="Ваше имя", f_ph_msg="Например: маникюр, Düsseldorf-Benrath", f_btn="Получить бесплатный аудит →",
    f_note="При отправке откроется ваша почтовая программа. Сайт не сохраняет никаких данных.",
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
    o.append('    <div class="pz-board" id="pz-board" role="group" aria-label="%s" data-img="%s"></div>\n  </div>\n  </div>\n' % (esc(z["alt"]), img))
    o.append('  <div class="pz-modal" id="pz-modal" role="dialog" aria-modal="true" aria-labelledby="pz-mt"><div class="pz-dialog">\n')
    o.append('    <button type="button" class="pz-x" id="pz-close" aria-label="%s">&times;</button>\n' % esc(z["close"]))
    o.append('    <h4 id="pz-mt">%s</h4>\n    <div class="pz-pass-l">%s</div>\n    <div class="pz-word">%s</div>\n' % (esc(z["m_title"]), esc(z["m_pass"]), esc(z["word"])))
    o.append('    <p>%s</p>\n    <div class="pz-acts"><a class="pz-a1" href="%s">%s</a><a class="pz-a2" href="%s" target="_blank" rel="noopener">%s</a></div>\n' % (esc(z["m_text"]), chk, esc(z["m_btn1"]), esc(wa), esc(z["m_btn2"])))
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
      if(solved()){done=true;board.classList.add('done');paint();setTimeout(openM,700);return}
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
  function load(){var u='url('+board.dataset.img+')';tiles.forEach(function(t){t.style.backgroundImage=u})}
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(en){if(en[0].isIntersecting){load();io.disconnect()}},{rootMargin:'400px'});io.observe(board);
  }else load();
  shuffle();
})();
  </script>
"""


WIDGET = """<script>(function () { var widget = document.createElement('script'); widget.defer = true; widget.dataset.pfId = 'e95ecb09-89d8-4863-b954-200bd0a8ed56'; widget.src = 'https://widget.yourgood.app/script/widget.js?id=e95ecb09-89d8-4863-b954-200bd0a8ed56&now='+Date.now(); document.head.appendChild(widget); })()</script>
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
    w('<link rel="preload" href="/fonts/dm-serif-display-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>\n')
    w('<style>\n/* Schriften lokal gehostet (keine Verbindung zu Google Fonts) */\n' + FONTS + CSS + PZ_CSS + '</style>\n</head>\n<body>\n\n')

    # header
    w('<header>\n  <nav class="wrap" aria-label="Navigation">\n')
    w('    <a class="brand" href="/%s"><span class="brand-init" aria-hidden="true">OP</span><span class="brand-name">Olha <span>Polishchuk</span></span></a>\n' % PATHS[lang])
    w('    <div class="nav-links">\n')
    for a, label in zip(ANCHORS, t["nav"]):
        w('      <a href="#%s">%s</a>\n' % (a, esc(label)))
    w('    </div>\n    <div class="nav-right">\n      <div class="lang-sw" role="group" aria-label="%s">' % esc(t["lang_name"]))
    for l2 in ("uk", "de", "ru"):
        cur = ' class="on" aria-current="page"' if l2 == lang else ''
        w('<a href="/%s" hreflang="%s" lang="%s" translate="no"%s>%s</a>' % (PATHS[l2], l2, l2, cur, LABELS[l2]))
    w('</div>\n      <a href="#contact" class="cta-nav">%s</a>\n    </div>\n  </nav>\n</header>\n\n' % esc(t["cta_nav"]))

    # hero
    w('<section class="hero" id="top">\n  <div class="wrap hero-inner">\n    <div class="hero-text">\n')
    w('      <div class="hero-eyebrow">%s</div>\n      <h1>%s</h1>\n      <p class="hero-sub">%s</p>\n' % (esc(t["eyebrow"]), t["h1"], esc(t["sub"])))
    w('      <div class="hero-btns">\n        <a href="#contact" class="btn-primary">%s</a>\n        <a href="#pakete" class="btn-outline">%s</a>\n      </div>\n    </div>\n' % (esc(t["btn1"]), esc(t["btn2"])))
    w('    <div class="hero-photo">\n      <div class="hero-photo-frame"><img src="/images/olha-portrait.jpg" width="900" height="1350" alt="%s" fetchpriority="high"></div>\n' % esc(t["photo_alt"]))
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
        w('        </ul>\n        <p class="pkg-term">%s</p>\n        <a href="#contact" class="pkg-btn">%s</a>\n      </article>\n' % (esc(p["term"]), esc(t["pk_btn"])))
    w('    </div>\n    <div class="pkg-extras">\n      <div class="pkg-extra">%s</div>\n      <div class="pkg-extra">%s</div>\n    </div>\n' % (t["pk_combo"], t["pk_addon"]))
    w('    <p class="pkg-note">%s</p>\n  </div>\n</section>\n\n' % esc(t["pk_note"]))

    # steps
    w('<section class="ablauf" id="ablauf">\n  <div class="wrap">\n    <div class="sec-label">%s</div>\n    <h2 class="sec-title">%s</h2>\n    <ol class="steps" style="list-style:none">\n' % (esc(t["st_label"]), esc(t["st_title"])))
    for i, (h, p) in enumerate(t["steps"], 1):
        w('      <li class="step"><div class="step-num" aria-hidden="true">%d</div><h3>%s</h3><p>%s</p></li>\n' % (i, esc(h), esc(p)))
    w('    </ol>\n  </div>\n</section>\n\n')

    # cases
    w('<section class="cases" id="ergebnisse">\n  <div class="wrap">\n    <div class="sec-label">%s</div>\n    <h2 class="sec-title">%s</h2>\n    <div class="cases-grid">\n' % (esc(t["cs_label"]), esc(t["cs_title"])))
    for c in t["cases"]:
        name = esc(c["name"])
        if c.get("link"):
            name = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (c["link"], name)
        w('      <div class="case%s">\n        <div class="case-tag">%s</div>\n        <h3>%s</h3>\n        <p>%s</p>\n        <div class="case-result">' % (" wide" if c.get("wide") else "", esc(c["tag"]), name, esc(c["text"])))
        for num, lbl in c["res"]:
            w('<div class="result-item"><div class="r-num">%s</div><div class="r-lbl">%s</div></div>' % (esc(num), esc(lbl)))
        w('</div>\n      </div>\n')
    w('    </div>\n    <p class="also">%s</p>\n  </div>\n</section>\n\n' % t["also"])

    # about
    w('<section class="about" id="about">\n  <div class="wrap about-grid">\n    <div class="about-img">\n')
    w('      <div class="about-img-frame"><img src="/images/olha-arbeit.jpg" width="1100" height="734" loading="lazy" alt="%s"></div>\n' % esc(t["ab_img_alt"]))
    w('      <div class="about-card"><div class="about-card-title">%s</div><div class="about-card-langs">' % esc(t["ab_langs"]))
    for color, nm, l2 in (("#000", "Deutsch", "de"), ("#005BBB", "Українська", "uk"), ("#CC0000", "Русский", "ru"), ("#00247D", "English", "en")):
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
    for q, a in t["faq"]:
        w('      <details><summary>%s</summary><p>%s</p></details>\n' % (esc(q), esc(a)))
    w('    </div>\n  </div>\n</section>\n\n')

    # contact
    w('<section class="contact" id="contact">\n  <div class="wrap contact-inner">\n    <div>\n')
    w('      <h2>%s</h2>\n      <p class="contact-sub">%s</p>\n      <div class="contact-methods">\n' % (t["ct_title"], esc(t["ct_sub"])))
    w('        <a class="cm wa" href="%s" target="_blank" rel="noopener" title="%s" aria-label="%s"><span class="cm-ic">%s</span></a>\n' % (esc(wa), esc(t["wa_label"]), esc(t["wa_label"]), ICON["wa"]))
    w('        <a class="cm" href="mailto:%s?subject=%%5BWebsite%%5D%%20Google-Check" title="E-Mail" aria-label="E-Mail"><span class="cm-ic">%s</span></a>\n' % (EMAIL, ICON["mail"]))
    w('        <a class="cm" href="%s" target="_blank" rel="noopener" title="LinkedIn" aria-label="LinkedIn"><span class="cm-ic">%s</span></a>\n' % (LINKEDIN, ICON["in"]))
    w('      </div>\n    </div>\n')
    w('    <form class="contact-form" onsubmit="return sendMsg(event)">\n      <h3>%s</h3>\n' % esc(t["f_title"]))
    w('      <div class="form-row"><label for="f-name">%s</label><input id="f-name" type="text" autocomplete="name" placeholder="%s"></div>\n' % (esc(t["f_name"]), esc(t["f_ph_name"])))
    w('      <div class="form-row"><label for="f-mail">%s</label><input id="f-mail" type="email" autocomplete="email" placeholder="name@email.de"></div>\n' % esc(t["f_mail"]))
    w('      <div class="form-row"><label for="f-msg">%s</label><textarea id="f-msg" placeholder="%s"></textarea></div>\n' % (esc(t["f_msg"]), esc(t["f_ph_msg"])))
    w('      <button type="submit" class="form-submit">%s</button>\n      <p class="form-note">%s <a href="/datenschutz.html">Datenschutz</a></p>\n    </form>\n  </div>\n</section>\n\n' % (esc(t["f_btn"]), esc(t["f_note"])))

    # footer
    w('<footer>\n  <div class="wrap foot-inner">\n    <div class="foot-copy">© 2026 Olha Polishchuk · Düsseldorf</div>\n    <div class="foot-links"><a href="/impressum.html">Impressum</a><a href="/datenschutz.html">Datenschutz</a><a href="%s" target="_blank" rel="noopener">LinkedIn</a></div>\n  </div>\n</footer>\n\n' % LINKEDIN)

    # script
    w('<script>\nfunction sendMsg(e){\n  e.preventDefault();\n')
    w('  var n=document.getElementById("f-name").value.trim(),m=document.getElementById("f-mail").value.trim(),t=document.getElementById("f-msg").value;\n')
    w('  if(!n||!m){alert(%s);return false;}\n' % json.dumps(t["f_alert"], ensure_ascii=False))
    w('  window.location.href="mailto:%s?subject="+encodeURIComponent("[Website] Google-Check: "+n+" (%s)")+"&body="+encodeURIComponent(t+"\\n\\nE-Mail: "+m);\n  return false;\n}\n</script>\n' % (EMAIL, LABELS[lang]))
    w(WIDGET + '</body>\n</html>\n')
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
