/**
 * Cloudflare Worker «seiten» — клиентские сайты «Website selbst» (olhapolishchuk.de), 20.11.2026
 *
 * Что делает:
 *  - отдаёт сайты клиенток: по своему домену (lumi-nails.de) или для проверки по адресу …workers.dev/s/<slug>/
 *    Шаблон берётся с https://olhapolishchuk.de/website-selbst/vorschau.html, данные и фото — из KV.
 *  - API для конструктора: клиентка по личной ссылке загружает свои данные, меняет, публикует (сразу).
 *  - после каждой публикации — письмо Оле со списком изменений; предыдущая версия хранится для отката.
 *  - /admin — страница для Оли: создать сайт из заявки, выдать/сменить ссылку для правок, домены, откат.
 *
 * Настройки (Cloudflare → Workers → seiten → Settings):
 *   KV binding   SITES          — KV-namespace «seiten»
 *   Secret       ADMIN_TOKEN    — пароль для /admin (длинный, случайный)
 *   Secret       BREVO_API_KEY  — тот же ключ, что у Worker «kontakt»
 *   Text         TO_EMAIL       — olha.polishchuk.web@gmail.com
 *   Text         FROM_EMAIL     — hello@olhapolishchuk.de
 *
 * Ключи в KV:
 *   site:<slug>   JSON {slug, hosts[], keyHash, data, created, updated, version}
 *   prev:<slug>   предыдущая версия (для отката)
 *   host:<домен>  slug
 *   img:<slug>:<id>  фото (bytes), metadata {type}
 */

const EDITOR_ORIGINS = ["https://olhapolishchuk.de", "https://www.olhapolishchuk.de"];
const EDITOR_URL = "https://olhapolishchuk.de/website-selbst/";
const TEMPLATE_URL = "https://olhapolishchuk.de/website-selbst/vorschau.html";
const ASSET_ORIGIN = "https://olhapolishchuk.de"; // шрифты и примерные фото: /demo/midna/…
const SLUG_RE = /^[a-z0-9](?:[a-z0-9-]{0,38}[a-z0-9])?$/;
const IMG_TYPES = { "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp" };
const MAX_IMG = 1_500_000;
const MAX_DATA = 60_000;

// ── helpers ─────────────────────────────────────────────────────────────────
const enc = new TextEncoder();
function cors(origin) {
  return {
    "Access-Control-Allow-Origin": EDITOR_ORIGINS.includes(origin) ? origin : EDITOR_ORIGINS[0],
    "Access-Control-Allow-Methods": "GET, PUT, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Edit-Key",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}
function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...extra } });
}
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function clean(v, max) {
  return String(v ?? "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").slice(0, max);
}
async function sha256(s) {
  const h = await crypto.subtle.digest("SHA-256", enc.encode(s));
  return [...new Uint8Array(h)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
function randomId(bytes) {
  const a = crypto.getRandomValues(new Uint8Array(bytes));
  return btoa(String.fromCharCode(...a)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function safeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}
function b64(str) {
  const bytes = enc.encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}
const getSite = async (env, slug) => (SLUG_RE.test(slug || "") ? env.SITES.get("site:" + slug, "json") : null);
const editUrl = (slug, key) => `${EDITOR_URL}#edit=${slug}.${key}`;

async function checkKey(env, slug, key) {
  const site = await getSite(env, slug);
  if (!site || !key) return null;
  return safeEqual(await sha256(key), site.keyHash) ? site : null;
}

// ── Daten prüfen und bereinigen (was der Baukasten schickt) ─────────────────
function sanitize(d) {
  if (!d || typeof d !== "object") return null;
  const s = (v, m) => clean(v, m);
  const out = {
    v: 1,
    siteLang: ["de", "uk", "ru"].includes(d.siteLang) ? d.siteLang : "de",
    scheme: ["kupfer", "rose", "salbei", "nacht"].includes(d.scheme) ? d.scheme : "kupfer",
    studio: s(d.studio, 40), category: s(d.category, 30), slogan: s(d.slogan, 90),
    street: s(d.street, 80), zip: s(d.zip, 5), city: s(d.city, 40), hours: s(d.hours, 300),
    phone: s(d.phone, 30), whatsapp: !!d.whatsapp, instagram: s(d.instagram, 60),
    ctaTitle: s(d.ctaTitle, 70), owner: s(d.owner, 40), about: s(d.about, 700),
    services: (Array.isArray(d.services) ? d.services : []).slice(0, 20).map((x) => ({
      name: s(x && x.name, 50), price: s(x && x.price, 16), desc: s(x && x.desc, 90),
    })),
    imp: {
      name: s(d.imp && d.imp.name, 80), company: s(d.imp && d.imp.company, 80), same: !(d.imp && d.imp.same === false),
      street: s(d.imp && d.imp.street, 80), zip: s(d.imp && d.imp.zip, 5), city: s(d.imp && d.imp.city, 40),
      phone: s(d.imp && d.imp.phone, 30), email: s(d.imp && d.imp.email, 120), ustid: s(d.imp && d.imp.ustid, 14),
      klein: !!(d.imp && d.imp.klein),
    },
    domain: s(d.domain, 63),
    images: { logo: "", hero: "", portrait: "", gallery: ["", "", "", ""], svc: [] },
  };
  const img = d.images && typeof d.images === "object" ? d.images : {};
  const id = (v) => (typeof v === "string" && /^[A-Za-z0-9_-]{6,40}\.(jpg|png|webp)$/.test(v) ? v : "");
  out.images.logo = id(img.logo); out.images.hero = id(img.hero); out.images.portrait = id(img.portrait);
  out.images.gallery = [0, 1, 2, 3].map((i) => id(Array.isArray(img.gallery) ? img.gallery[i] : ""));
  out.images.svc = (Array.isArray(img.svc) ? img.svc : []).slice(0, 4).map(id);
  return out;
}
function missing(d) {
  const m = [];
  const street = d.imp.same ? d.street : d.imp.street, zip = d.imp.same ? d.zip : d.imp.zip, city = d.imp.same ? d.city : d.imp.city;
  if (!d.studio.trim()) m.push("Name des Studios");
  if (!d.phone.trim()) m.push("Telefon");
  if (!d.services.some((x) => x.name.trim() && x.price.trim())) m.push("Leistung mit Preis");
  if (!d.imp.name.trim()) m.push("Impressum: Name");
  if (!street.trim() || !zip.trim() || !city.trim()) m.push("Impressum: Anschrift");
  if (!/^[^\s@<>"]+@[^\s@<>"]+\.[^\s@<>"]{2,}$/.test(d.imp.email.trim())) m.push("Impressum: E-Mail");
  return m;
}

// ── Liste der Änderungen für die E-Mail ─────────────────────────────────────
const LABEL = {
  siteLang: "Sprache", scheme: "Farbschema", studio: "Name", category: "Art des Studios", slogan: "Slogan", street: "Straße",
  zip: "PLZ", city: "Ort", hours: "Öffnungszeiten", phone: "Telefon", whatsapp: "WhatsApp", instagram: "Instagram",
  ctaTitle: "Satz vor Kontakt", owner: "Name (Über mich)", about: "Über mich", domain: "Domain",
  "imp.name": "Impressum: Name", "imp.company": "Impressum: Firma", "imp.same": "Impressum: Anschrift wie Studio",
  "imp.street": "Impressum: Straße", "imp.zip": "Impressum: PLZ", "imp.city": "Impressum: Ort", "imp.phone": "Impressum: Telefon",
  "imp.email": "Impressum: E-Mail", "imp.ustid": "Impressum: USt-IdNr.", "imp.klein": "Impressum: Kleinunternehmer",
};
function flat(o, p = "", r = {}) {
  for (const [k, v] of Object.entries(o || {})) {
    const key = p ? p + "." + k : k;
    if (v && typeof v === "object" && !Array.isArray(v)) flat(v, key, r);
    else r[key] = Array.isArray(v) ? JSON.stringify(v) : v;
  }
  return r;
}
function diff(a, b) {
  const out = [];
  const short = (v) => { v = String(v ?? "").replace(/\s+/g, " ").trim(); return v.length > 120 ? v.slice(0, 117) + "…" : v || "—"; };
  const fa = flat({ ...a, services: undefined, images: undefined }), fb = flat({ ...b, services: undefined, images: undefined });
  for (const k of new Set([...Object.keys(fa), ...Object.keys(fb)])) {
    if (k === "v" || String(fa[k] ?? "") === String(fb[k] ?? "")) continue;
    out.push(`${LABEL[k] || k}: „${short(fa[k])}“ → „${short(fb[k])}“`);
  }
  const sv = (x) => (x || []).filter((s) => s.name || s.price).map((s) => `${s.name} – ${s.price}${s.desc ? " (" + s.desc + ")" : ""}`);
  const sa = sv(a.services), sb = sv(b.services);
  sa.filter((x) => !sb.includes(x)).forEach((x) => out.push(`Leistung entfernt/geändert: ${x}`));
  sb.filter((x) => !sa.includes(x)).forEach((x) => out.push(`Leistung neu/geändert: ${x}`));
  const ia = flat(a.images || {}), ib = flat(b.images || {});
  const nameImg = { logo: "Logo", hero: "Titelbild", portrait: "Foto Über mich", gallery: "Galerie", svc: "Fotos Leistungen" };
  for (const k of Object.keys(nameImg)) if (String(ia[k] ?? "") !== String(ib[k] ?? "")) out.push(`Foto geändert: ${nameImg[k]}`);
  return out;
}

async function mail(env, subject, text, replyTo) {
  if (!env.BREVO_API_KEY) return false;
  const r = await fetch("https://api.brevo.com/v3/smtp/email", {
    method: "POST",
    headers: { "api-key": env.BREVO_API_KEY, "Content-Type": "application/json", "Accept": "application/json" },
    body: JSON.stringify({
      sender: { email: env.FROM_EMAIL, name: "Website selbst · olhapolishchuk.de" },
      to: [{ email: env.TO_EMAIL, name: "Olha Polishchuk" }],
      ...(replyTo ? { replyTo } : {}),
      subject, textContent: text, tags: ["website-selbst-aenderung"],
    }),
  });
  if (!r.ok) console.log("Brevo error", r.status, (await r.text()).slice(0, 300));
  return r.ok;
}

// неиспользуемые фото удаляем (после публикации и при откате не трогаем prev)
async function cleanupImages(env, slug, keep) {
  const keepSet = new Set(keep.filter(Boolean));
  let cursor;
  do {
    const l = await env.SITES.list({ prefix: `img:${slug}:`, cursor });
    for (const k of l.keys) if (!keepSet.has(k.name.split(":")[2])) await env.SITES.delete(k.name);
    cursor = l.list_complete ? null : l.cursor;
  } while (cursor);
}
const imgIds = (d) => d && d.images ? [d.images.logo, d.images.hero, d.images.portrait, ...(d.images.gallery || []), ...(d.images.svc || [])] : [];

// ── API: Baukasten ──────────────────────────────────────────────────────────
async function api(req, env, url, ctx) {
  const origin = req.headers.get("Origin") || "";
  const h = cors(origin);
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: h });
  if (!EDITOR_ORIGINS.includes(origin)) return json({ ok: false, error: "origin" }, 403, h);
  const slug = url.searchParams.get("slug") || "";
  const key = req.headers.get("X-Edit-Key") || "";

  if (url.pathname === "/api/site" && req.method === "GET") {
    const site = await checkKey(env, slug, key);
    if (!site) return json({ ok: false, error: "key" }, 403, h);
    return json({ ok: true, slug, hosts: site.hosts || [], data: site.data, updated: site.updated, imgBase: `${url.origin}/img/${slug}/` }, 200, h);
  }

  if (url.pathname === "/api/img" && req.method === "POST") {
    const site = await checkKey(env, slug, key);
    if (!site) return json({ ok: false, error: "key" }, 403, h);
    const type = (req.headers.get("Content-Type") || "").split(";")[0];
    if (!IMG_TYPES[type]) return json({ ok: false, error: "type" }, 415, h);
    const buf = await req.arrayBuffer();
    if (!buf.byteLength || buf.byteLength > MAX_IMG) return json({ ok: false, error: "size" }, 413, h);
    const id = randomId(9) + "." + IMG_TYPES[type];
    await env.SITES.put(`img:${slug}:${id}`, buf, { metadata: { type } });
    return json({ ok: true, id, url: `${url.origin}/img/${slug}/${id}` }, 200, h);
  }

  if (url.pathname === "/api/site" && req.method === "PUT") {
    if (Number(req.headers.get("Content-Length") || 0) > MAX_DATA) return json({ ok: false, error: "too_large" }, 413, h);
    let body;
    try { body = await req.json(); } catch { return json({ ok: false, error: "bad_json" }, 400, h); }
    const site = await checkKey(env, String(body.slug || ""), String(body.key || ""));
    if (!site) return json({ ok: false, error: "key" }, 403, h);
    if (body.confirm !== true) return json({ ok: false, error: "confirm" }, 422, h);
    const data = sanitize(body.data);
    if (!data) return json({ ok: false, error: "invalid" }, 422, h);
    data.domain = site.data.domain; // Domain ändert nur Olha
    const miss = missing(data);
    if (miss.length) return json({ ok: false, error: "missing", missing: miss }, 422, h);
    const changes = diff(site.data, data);
    if (!changes.length) return json({ ok: true, unchanged: true, url: siteUrl(site, url) }, 200, h);
    const next = { ...site, data, updated: new Date().toISOString(), version: (site.version || 1) + 1 };
    await env.SITES.put("prev:" + site.slug, JSON.stringify(site));
    await env.SITES.put("site:" + site.slug, JSON.stringify(next));
    const when = new Date().toLocaleString("de-DE", { timeZone: "Europe/Berlin" });
    const text =
      `${data.studio} hat die Website geändert (Version ${next.version}, ${when}).\n` +
      `Website: ${siteUrl(next, url)}\n\n` +
      `ÄNDERUNGEN:\n- ${changes.join("\n- ")}\n\n` +
      `Bestätigt: Kundin ist für Texte und Fotos verantwortlich ✓\n\n` +
      `Etwas stimmt nicht? Rückgängig machen: ${url.origin}/admin → „${site.slug}“ → «Откатить».\n` +
      `Antworten geht direkt an ${data.imp.email}.`;
    const work = Promise.all([
      mail(env, `[Website selbst] Änderung: ${data.studio} (${changes.length})`, text, { email: data.imp.email, name: data.imp.name }),
      cleanupImages(env, site.slug, [...imgIds(data), ...imgIds(site.data)]),
    ]);
    if (ctx && ctx.waitUntil) ctx.waitUntil(work); else await work;
    return json({ ok: true, url: siteUrl(next, url), version: next.version }, 200, h);
  }
  return json({ ok: false, error: "not_found" }, 404, h);
}
function siteUrl(site, url) {
  return site.hosts && site.hosts[0] ? `https://${site.hosts[0]}/` : `${url.origin}/s/${site.slug}/`;
}

// ── API: Admin (nur Olha) ───────────────────────────────────────────────────
async function admin(req, env, url) {
  const tok = req.headers.get("X-Admin-Token") || "";
  if (!env.ADMIN_TOKEN || !safeEqual(tok, env.ADMIN_TOKEN)) return json({ ok: false, error: "auth" }, 403);
  const body = req.method === "POST" ? await req.json().catch(() => ({})) : {};
  const slug = String(body.slug || url.searchParams.get("slug") || "").toLowerCase();
  const op = url.pathname.replace("/api/admin/", "");

  if (op === "sites") {
    const out = [];
    let cursor;
    do {
      const l = await env.SITES.list({ prefix: "site:", cursor });
      for (const k of l.keys) {
        const s = await env.SITES.get(k.name, "json");
        if (s) out.push({ slug: s.slug, studio: s.data.studio, hosts: s.hosts || [], updated: s.updated, version: s.version, url: siteUrl(s, url) });
      }
      cursor = l.list_complete ? null : l.cursor;
    } while (cursor);
    return json({ ok: true, sites: out });
  }
  if (op === "create") {
    if (!SLUG_RE.test(slug)) return json({ ok: false, error: "Slug: nur a–z, 0–9 und Bindestrich" }, 422);
    if (await env.SITES.get("site:" + slug)) return json({ ok: false, error: "Slug existiert schon" }, 409);
    let raw = body.data;
    if (typeof raw === "string") { try { raw = JSON.parse(raw); } catch { return json({ ok: false, error: "JSON fehlerhaft" }, 422); } }
    if (raw && raw.site) raw = raw.site; // ganze Anfrage eingefügt
    const data = sanitize(raw);
    if (!data) return json({ ok: false, error: "Daten fehlen" }, 422);
    const key = randomId(18);
    const now = new Date().toISOString();
    await env.SITES.put("site:" + slug, JSON.stringify({ slug, hosts: [], keyHash: await sha256(key), data, created: now, updated: now, version: 1 }));
    return json({ ok: true, slug, editUrl: editUrl(slug, key), url: `${url.origin}/s/${slug}/`, missing: missing(data) });
  }
  const site = await getSite(env, slug);
  if (!site) return json({ ok: false, error: "Seite nicht gefunden" }, 404);
  if (op === "key") {
    const key = randomId(18);
    await env.SITES.put("site:" + slug, JSON.stringify({ ...site, keyHash: await sha256(key) }));
    return json({ ok: true, editUrl: editUrl(slug, key) });
  }
  if (op === "hosts") {
    const hosts = (Array.isArray(body.hosts) ? body.hosts : String(body.hosts || "").split(/[\s,]+/))
      .map((x) => String(x).trim().toLowerCase().replace(/^https?:\/\//, "").replace(/\/.*$/, "")).filter((x) => /^[a-z0-9.-]+\.[a-z]{2,}$/.test(x)).slice(0, 4);
    for (const old of site.hosts || []) if (!hosts.includes(old)) await env.SITES.delete("host:" + old);
    for (const hst of hosts) await env.SITES.put("host:" + hst, slug);
    await env.SITES.put("site:" + slug, JSON.stringify({ ...site, hosts }));
    return json({ ok: true, hosts });
  }
  if (op === "rollback") {
    const prev = await env.SITES.get("prev:" + slug, "json");
    if (!prev) return json({ ok: false, error: "Keine frühere Version" }, 404);
    // Schlüssel und Domains bleiben die aktuellen
    await env.SITES.put("site:" + slug, JSON.stringify({ ...prev, keyHash: site.keyHash, hosts: site.hosts, updated: new Date().toISOString(), version: (site.version || 1) + 1 }));
    await env.SITES.put("prev:" + slug, JSON.stringify(site));
    return json({ ok: true });
  }
  if (op === "export") return json({ ok: true, site: { ...site, keyHash: undefined } });
  if (op === "delete") {
    for (const hst of site.hosts || []) await env.SITES.delete("host:" + hst);
    await cleanupImages(env, slug, []);
    await env.SITES.delete("site:" + slug);
    await env.SITES.delete("prev:" + slug);
    return json({ ok: true });
  }
  return json({ ok: false, error: "unbekannt" }, 404);
}

// ── Seiten ausliefern ───────────────────────────────────────────────────────
async function template() {
  const r = await fetch(TEMPLATE_URL, { cf: { cacheTtl: 300, cacheEverything: true } });
  if (!r.ok) throw new Error("template " + r.status);
  return r.text();
}
async function renderSite(site, rest, url, isCustom) {
  let html = await template();
  const d = site.data;
  const legal = rest === "impressum" ? "imp" : rest === "datenschutz" ? "ds" : "";
  const base = isCustom ? "/" : `/s/${site.slug}/`;
  const payload = { data: d, imgBase: `/img/${site.slug}/`, base, legal, updated: site.updated };
  const title = legal === "imp" ? `Impressum · ${d.studio}` : legal === "ds" ? `Datenschutz · ${d.studio}` : [d.studio, d.category, d.city].filter(Boolean).join(" · ");
  const desc = (d.slogan || [d.category, d.city].filter(Boolean).join(" in ")).slice(0, 160);
  const canon = isCustom ? `https://${url.hostname}/${rest}` : "";
  const robots = isCustom ? "index, follow" : "noindex, nofollow";
  const ld = {
    "@context": "https://schema.org", "@type": "BeautySalon", name: d.studio, telephone: d.phone || undefined,
    address: { "@type": "PostalAddress", streetAddress: d.street, postalCode: d.zip, addressLocality: d.city, addressCountry: "DE" },
    url: canon ? `https://${url.hostname}/` : undefined, sameAs: d.instagram ? [`https://www.instagram.com/${d.instagram.replace(/^@/, "")}/`] : undefined,
  };
  html = html
    .replace(/<html lang="[^"]*">/, `<html lang="${d.siteLang || "de"}">`)
    .replace(/<meta name="robots"[^>]*>/, `<meta name="robots" content="${robots}">`)
    .replace(/<title>[\s\S]*?<\/title>/, `<title>${esc(title)}</title>\n<meta name="description" content="${esc(desc)}">` +
      (canon ? `\n<link rel="canonical" href="${esc(canon)}">` : "") +
      `\n<script type="application/ld+json">${JSON.stringify(ld).replace(/</g, "\\u003c")}</script>`)
    .replace("<script>\nconst A=", `<script>window.SITE=${JSON.stringify(payload).replace(/</g, "\\u003c")};</script>\n<script>\nconst A=`);
  return new Response(html, {
    headers: {
      "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-cache",
      "X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin",
      ...(isCustom ? {} : { "X-Robots-Tag": "noindex" }),
    },
  });
}
async function serveImg(env, slug, id, req, ctx) {
  const cache = typeof caches !== "undefined" ? caches.default : null;
  if (cache) { const hit = await cache.match(req); if (hit) return hit; }
  const { value, metadata } = await env.SITES.getWithMetadata(`img:${slug}:${id}`, "arrayBuffer");
  if (!value) return new Response("Not found", { status: 404 });
  const res = new Response(value, { headers: {
    "Content-Type": (metadata && metadata.type) || "image/jpeg", "Cache-Control": "public, max-age=31536000, immutable",
    "X-Content-Type-Options": "nosniff", "Access-Control-Allow-Origin": "*",
  } });
  if (cache && ctx && ctx.waitUntil) ctx.waitUntil(cache.put(req, res.clone()));
  return res;
}
async function proxyAsset(path) {
  if (!/^\/demo\/midna\/(fonts\/[a-z0-9-]+\.woff2|img\/[a-z0-9-]+\.(webp|jpg))$/.test(path)) return new Response("Not found", { status: 404 });
  const r = await fetch(ASSET_ORIGIN + path, { cf: { cacheTtl: 86400, cacheEverything: true } });
  return new Response(r.body, { status: r.status, headers: {
    "Content-Type": r.headers.get("Content-Type") || "application/octet-stream", "Cache-Control": "public, max-age=604800",
  } });
}

// ── Router ──────────────────────────────────────────────────────────────────
export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const p = url.pathname;
    try {
      if (p.startsWith("/api/admin/")) return await admin(req, env, url);
      if (p.startsWith("/api/")) return await api(req, env, url, ctx);
      const mImg = p.match(/^\/img\/([a-z0-9-]+)\/([A-Za-z0-9_-]+\.(?:jpg|png|webp))$/);
      if (mImg) return await serveImg(env, mImg[1], mImg[2], req, ctx);
      const asset = p.indexOf("/demo/midna/");
      if (asset >= 0) return await proxyAsset(p.slice(asset));

      // eigene Domain der Kundin?
      const host = url.hostname.toLowerCase();
      const hostSlug = await env.SITES.get("host:" + host);
      if (hostSlug) {
        const site = await getSite(env, hostSlug);
        if (!site) return new Response("Seite nicht gefunden", { status: 404 });
        if (site.hosts && site.hosts[0] && site.hosts[0] !== host) return Response.redirect(`https://${site.hosts[0]}${p}`, 301);
        const rest = p.replace(/^\/+|\/+$/g, "");
        if (rest === "robots.txt") return new Response(`User-agent: *\nAllow: /\nSitemap: https://${host}/sitemap.xml\n`, { headers: { "Content-Type": "text/plain" } });
        if (rest === "sitemap.xml") return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://${host}/</loc><lastmod>${(site.updated || "").slice(0, 10)}</lastmod></url><url><loc>https://${host}/impressum</loc></url><url><loc>https://${host}/datenschutz</loc></url></urlset>`, { headers: { "Content-Type": "application/xml" } });
        if (!["", "impressum", "datenschutz"].includes(rest)) return Response.redirect(`https://${host}/`, 302);
        return await renderSite(site, rest, url, true);
      }

      if (p === "/admin" || p === "/admin/") return new Response(ADMIN_HTML, { headers: { "Content-Type": "text/html; charset=utf-8", "X-Robots-Tag": "noindex", "Cache-Control": "no-store" } });

      // Testadresse: /s/<slug>/[impressum|datenschutz]
      const m = p.match(/^\/s\/([a-z0-9-]+)(\/.*)?$/);
      if (m) {
        if (!m[2]) return Response.redirect(`${url.origin}/s/${m[1]}/`, 301);
        const site = await getSite(env, m[1]);
        if (!site) return new Response("Seite nicht gefunden", { status: 404 });
        const rest = m[2].replace(/^\/+|\/+$/g, "");
        if (!["", "impressum", "datenschutz"].includes(rest)) return Response.redirect(`${url.origin}/s/${m[1]}/`, 302);
        return await renderSite(site, rest, url, false);
      }
      if (p === "/") return Response.redirect(EDITOR_URL, 302);
      return new Response("Not found", { status: 404 });
    } catch (e) {
      console.log("error", e && e.stack || e);
      return new Response("Fehler – bitte später erneut versuchen.", { status: 500 });
    }
  },
};

// ── /admin (Seite für Olha) ─────────────────────────────────────────────────
const ADMIN_HTML = `<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex">
<title>Website selbst · Admin</title>
<style>
*{box-sizing:border-box}body{margin:0;font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif;background:#F7F6F4;color:#1E2A4A}
header{background:#1E2A4A;color:#fff;padding:12px 18px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}header b{margin-right:auto}
main{max-width:980px;margin:0 auto;padding:18px}section{background:#fff;border:1px solid rgba(30,42,74,.12);border-radius:12px;padding:18px;margin-bottom:16px}
h2{font-size:17px;margin:0 0 10px}input,textarea{width:100%;font:inherit;padding:9px 11px;border:1px solid rgba(30,42,74,.25);border-radius:8px;margin:4px 0 10px}
textarea{min-height:140px;font:12px/1.4 ui-monospace,monospace}button{font:inherit;font-weight:600;border:0;border-radius:8px;padding:9px 14px;background:#1E2A4A;color:#fff;cursor:pointer}
button.alt{background:#fff;color:#1E2A4A;border:1px solid rgba(30,42,74,.3)}button.warn{background:#fff;color:#B42318;border:1px solid #F1B5AE}
table{width:100%;border-collapse:collapse;font-size:14px}td,th{padding:8px 6px;border-bottom:1px solid rgba(30,42,74,.1);text-align:left;vertical-align:top}
td .acts{display:flex;gap:6px;flex-wrap:wrap}.out{background:#FDF3E7;border:1px solid #F1D8B8;border-radius:8px;padding:10px;word-break:break-all;display:none;margin-top:10px}
.out.on{display:block}.err{color:#B42318}small{color:#4A5568}.row{display:grid;grid-template-columns:1fr 1fr;gap:10px}@media(max-width:640px){.row{grid-template-columns:1fr}}
</style></head><body>
<header><b>Website selbst · Admin</b><input id="tok" type="password" placeholder="ADMIN_TOKEN" style="max-width:260px;margin:0"><button id="login" class="alt">Войти</button></header>
<main>
<section><h2>Сайты</h2><div id="list"><small>Введите пароль сверху.</small></div><div class="out" id="out"></div></section>
<section><h2>Новый сайт из заявки</h2>
<div class="row"><label>Slug (адрес для проверки, a–z, 0–9, -)<input id="slug" placeholder="lumi-nails"></label>
<label>Домен (можно позже)<input id="hosts" placeholder="lumi-nails.de www.lumi-nails.de"></label></div>
<label>JSON из письма (вложение website-selbst-….json)<textarea id="data" placeholder="{ … }"></textarea></label>
<button id="create">Создать сайт</button> <small>После создания: ссылку для правок отправьте клиентке (WhatsApp/E-Mail). Фото она загружает сама.</small>
<div class="out" id="cout"></div></section>
</main>
<script>
const $=s=>document.querySelector(s);let T=sessionStorage.getItem("ws-admin")||"";$("#tok").value=T;
const api=(op,body)=>fetch("/api/admin/"+op,{method:body?"POST":"GET",headers:{"X-Admin-Token":T,"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined}).then(r=>r.json());
const e=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function show(el,html){el.innerHTML=html;el.classList.add("on")}
async function load(){const r=await api("sites");if(!r.ok){$("#list").innerHTML='<p class="err">Неверный пароль.</p>';return}
 $("#list").innerHTML=r.sites.length?'<table><tr><th>Сайт</th><th>Домен</th><th>Изменён</th><th></th></tr>'+r.sites.map(s=>'<tr><td><b>'+e(s.studio)+'</b><br><a href="'+e(s.url)+'" target="_blank">'+e(s.slug)+' ↗</a></td><td>'+e(s.hosts.join(", ")||"—")+'</td><td>'+e((s.updated||"").slice(0,16).replace("T"," "))+'<br><small>v'+e(s.version)+'</small></td><td><div class="acts" data-s="'+e(s.slug)+'"><button class="alt" data-a="key">Новая ссылка</button><button class="alt" data-a="hosts">Домен</button><button class="alt" data-a="export">JSON</button><button class="warn" data-a="rollback">Откатить</button><button class="warn" data-a="delete">Удалить</button></div></td></tr>').join("")+'</table>':'<small>Пока нет сайтов.</small>'}
$("#login").onclick=()=>{T=$("#tok").value.trim();sessionStorage.setItem("ws-admin",T);load()};
$("#list").onclick=async ev=>{const b=ev.target.closest("button[data-a]");if(!b)return;const slug=b.parentNode.dataset.s,a=b.dataset.a,out=$("#out");
 if(a==="key"){if(!confirm("Старая ссылка перестанет работать. Создать новую?"))return;const r=await api("key",{slug});show(out,r.ok?'Новая ссылка для правок <b>'+e(slug)+'</b>:<br><a href="'+e(r.editUrl)+'" target="_blank">'+e(r.editUrl)+'</a>':'<span class="err">'+e(r.error)+'</span>')}
 if(a==="hosts"){const h=prompt("Домены через пробел (первый — главный), напр. lumi-nails.de www.lumi-nails.de");if(h===null)return;const r=await api("hosts",{slug,hosts:h});show(out,r.ok?"Домены: "+e(r.hosts.join(", ")||"—")+"<br><small>В Cloudflare: Workers → seiten → Settings → Domains &amp; Routes → Add Custom Domain (для каждого).</small>":'<span class="err">'+e(r.error)+'</span>');load()}
 if(a==="export"){const r=await api("export?slug="+encodeURIComponent(slug));show(out,'<textarea>'+e(JSON.stringify(r.site,null,2))+'</textarea>')}
 if(a==="rollback"){if(!confirm("Вернуть предыдущую версию сайта "+slug+"?"))return;const r=await api("rollback",{slug});show(out,r.ok?"Откат сделан ✓":'<span class="err">'+e(r.error)+'</span>');load()}
 if(a==="delete"){if(prompt("Сайт и все фото будут удалены. Для подтверждения введите slug:")!==slug)return;const r=await api("delete",{slug});show(out,r.ok?"Удалено.":'<span class="err">'+e(r.error)+'</span>');load()}};
$("#create").onclick=async()=>{const r=await api("create",{slug:$("#slug").value.trim(),data:$("#data").value});const o=$("#cout");
 if(!r.ok){show(o,'<span class="err">'+e(r.error)+'</span>');return}
 if($("#hosts").value.trim())await api("hosts",{slug:r.slug,hosts:$("#hosts").value});
 show(o,'Создано ✓ Проверка: <a href="'+e(r.url)+'" target="_blank">'+e(r.url)+'</a><br><br><b>Ссылка для правок</b> (отправить клиентке, хранить в секрете):<br><a href="'+e(r.editUrl)+'" target="_blank">'+e(r.editUrl)+'</a>'+(r.missing&&r.missing.length?'<p class="err">Не заполнено: '+e(r.missing.join(", "))+'</p>':''));load()};
if(T)load();
</script></body></html>`;
