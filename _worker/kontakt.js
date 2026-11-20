/**
 * Cloudflare Worker «kontakt» — принимает заявку с формы olhapolishchuk.de
 * и отправляет её письмом через Brevo (API транзакционных писем).
 *
 * Настройки в Cloudflare → Workers → kontakt → Settings → Variables and Secrets:
 *   BREVO_API_KEY  (Secret)  — ключ из Brevo: SMTP & API → API Keys
 *   TO_EMAIL       (Text)    — куда приходят заявки, напр. olha.polishchuk.web@gmail.com
 *   FROM_EMAIL     (Text)    — отправитель, подтверждённый в Brevo, напр. hello@olhapolishchuk.de
 *
 * Ничего не хранится: заявка сразу уходит письмом, в Worker остаются только технические логи Cloudflare.
 *
 * 20.11.2026: + заявки конструктора «Website selbst» (/website-selbst/, поле kind = "website-selbst").
 * Письмо с текстом заявки + вложение website-selbst.json (все поля). Фото не передаются — клиент шлёт их в WhatsApp.
 */

const ALLOWED_ORIGINS = [
  "https://olhapolishchuk.de",
  "https://www.olhapolishchuk.de",
];
const LANG_LABEL = { de: "DE", uk: "UA", ru: "RU" };
const TERMIN_RE = /^(\d{4})-(\d{2})-(\d{2}) (\d{2}:\d{2})$/;
const EMAIL_RE = /^[^\s@<>"]+@[^\s@<>"]+\.[^\s@<>"]{2,}$/;

function cors(origin) {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0],
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function json(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...cors(origin) },
  });
}

function clean(v, max) {
  return String(v ?? "").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, "").trim().slice(0, max);
}

// ── Конструктор «Website selbst» ───────────────────────────────────────────
function b64(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

async function websiteSelbst(data, env, origin) {
  const s = data.site && typeof data.site === "object" ? data.site : null;
  if (!s) return json({ ok: false, error: "invalid" }, 422, origin);
  const imp = s.imp && typeof s.imp === "object" ? s.imp : {};
  const ok = s.ok && typeof s.ok === "object" ? s.ok : {};
  const one = (v, max) => clean(v, max).replace(/[\r\n]+/g, " ");

  const studio = one(s.studio, 60);
  const name = one(imp.name, 100);
  const email = clean(imp.email, 200);
  const same = imp.same !== false;
  const street = one(same ? s.street : imp.street, 100);
  const zip = one(same ? s.zip : imp.zip, 10);
  const city = one(same ? s.city : imp.city, 60);
  const phone = one(imp.phone || s.phone, 40);
  const domain = one(s.domain, 70).toLowerCase();
  const lang = LANG_LABEL[data.lang] || "DE";

  // Pflichtangaben wie im Formular — sonst keine Anfrage
  if (!studio || !name || !EMAIL_RE.test(email) || !street || !zip || !city || !phone ||
      !(ok.photos && ok.content && ok.terms)) {
    return json({ ok: false, error: "invalid" }, 422, origin);
  }

  const services = (Array.isArray(s.services) ? s.services : []).slice(0, 20)
    .filter((x) => x && clean(x.name, 60))
    .map((x) => `- ${one(x.name, 60)} – ${one(x.price, 20) || "?"}${clean(x.desc, 100) ? " (" + one(x.desc, 100) + ")" : ""}`);

  const when = new Date().toLocaleString("de-DE", { timeZone: "Europe/Berlin" });
  const text =
    `Neue Anfrage „Website selbst“ über olhapolishchuk.de (${lang})\n\n` +
    `STUDIO:   ${studio} (${one(s.category, 40) || "—"})\n` +
    `DOMAIN:   ${domain || "— (noch keine)"}  → vor der Rechnung bei DENIC prüfen\n` +
    `Sprache:  ${one(s.siteLang, 5) || "de"} · Farbschema: ${one(s.scheme, 20) || "kupfer"}\n` +
    `Slogan:   ${one(s.slogan, 120) || "—"}\n` +
    `Adresse:  ${[one(s.street, 100), [one(s.zip, 10), one(s.city, 60)].filter(Boolean).join(" ")].filter(Boolean).join(", ") || "—"}\n` +
    `Telefon:  ${one(s.phone, 40) || "—"}${s.whatsapp ? " (WhatsApp)" : ""} · Instagram: ${one(s.instagram, 80) || "—"}\n` +
    `Zeiten:   ${clean(s.hours, 300).replace(/\n+/g, " / ") || "—"}\n\n` +
    `LEISTUNGEN:\n${services.join("\n") || "—"}\n\n` +
    `ÜBER MICH (${one(s.owner, 60) || "—"}):\n${clean(s.about, 800) || "—"}\n\n` +
    `IMPRESSUM:\n${name}${imp.company ? " / " + one(imp.company, 100) : ""}\n${street}, ${zip} ${city}\n` +
    `Tel: ${phone} · E-Mail: ${email}\nUSt-IdNr: ${one(imp.ustid, 20) || "—"} · Kleinunternehmer: ${imp.klein ? "ja" : "nein"}\n\n` +
    `BESTÄTIGT: Fotorechte ✓ · Inhalte/Impressum in eigener Verantwortung ✓ · Bedingungen + Unternehmer (§ 14 BGB) ✓\n\n` +
    (clean(s.note, 600) ? `NACHRICHT:\n${clean(s.note, 600)}\n\n` : "") +
    `Vor Veröffentlichung: Texte prüfen (HWG/UWG – keine Heilversprechen, kein Vorher/Nachher).\n` +
    `Neuen Kundensite anlegen: https://seiten.olha-polishchuk-web.workers.dev/admin → JSON aus dem Anhang einfügen. Fotos lädt die Kundin danach selbst über ihren Link hoch.\n\n` +
    `Zeit: ${when}\nAntworten: einfach auf diese E-Mail antworten (geht direkt an ${email}).`;

  const attachment = JSON.stringify(s, null, 2).slice(0, 50000);
  const fileBase = (domain || studio).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 40) || "anfrage";

  const res = await fetch("https://api.brevo.com/v3/smtp/email", {
    method: "POST",
    headers: { "api-key": env.BREVO_API_KEY, "Content-Type": "application/json", "Accept": "application/json" },
    body: JSON.stringify({
      sender: { email: env.FROM_EMAIL, name: "Website olhapolishchuk.de" },
      to: [{ email: env.TO_EMAIL, name: "Olha Polishchuk" }],
      replyTo: { email, name },
      subject: `[Website selbst] ${studio} – ${domain || "ohne Domain"} (${lang})`,
      textContent: text,
      attachment: [{ name: `website-selbst-${fileBase}.json`, content: b64(attachment) }],
      tags: ["website-selbst"],
    }),
  });
  if (!res.ok) {
    console.log("Brevo error (website-selbst)", res.status, (await res.text()).slice(0, 500));
    return json({ ok: false, error: "send" }, 502, origin);
  }
  return json({ ok: true }, 200, origin);
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
    if (request.method !== "POST") return json({ ok: false, error: "method" }, 405, origin);
    if (!ALLOWED_ORIGINS.includes(origin)) return json({ ok: false, error: "origin" }, 403, origin);

    const len = Number(request.headers.get("Content-Length") || 0);
    if (len > 60000) return json({ ok: false, error: "too_large" }, 413, origin);

    let data;
    try {
      data = await request.json();
    } catch {
      return json({ ok: false, error: "bad_json" }, 400, origin);
    }

    // Ловушка для ботов: скрытое поле заполнено или форма отправлена быстрее 3 секунд →
    // отвечаем «ок», но письмо не отправляем (бот не узнает, что его отсеяли).
    if (clean(data.website, 200) || Number(data.ms) < 3000) return json({ ok: true }, 200, origin);

    if (data.kind === "website-selbst") return websiteSelbst(data, env, origin);

    const name = clean(data.name, 100).replace(/[\r\n]+/g, " ");
    const email = clean(data.email, 200);
    const message = clean(data.message, 3000);
    const lang = LANG_LABEL[data.lang] || "DE";
    const page = clean(data.page, 200);

    // Wunschtermin aus dem Kalender (optional), Format «2026-11-16 12:00» → «Mo., 16.11.2026, 12:00 Uhr»
    let termin = "";
    const tm = TERMIN_RE.exec(clean(data.termin, 20));
    if (tm) {
      const d = new Date(Date.UTC(+tm[1], +tm[2] - 1, +tm[3]));
      termin = d.toLocaleDateString("de-DE", { weekday: "short", day: "2-digit", month: "2-digit", year: "numeric", timeZone: "UTC" }) + ", " + tm[4] + " Uhr";
    }

    if (!name || !EMAIL_RE.test(email)) return json({ ok: false, error: "invalid" }, 422, origin);

    const when = new Date().toLocaleString("de-DE", { timeZone: "Europe/Berlin" });
    const text =
      `Neue Anfrage über olhapolishchuk.de (${lang})\n\n` +
      (termin ? `WUNSCHTERMIN: ${termin}\n(noch nicht bestätigt – bitte per E-Mail bestätigen oder Alternative vorschlagen)\n\n` : "") +
      `Name:   ${name}\nE-Mail: ${email}\n\n` +
      `Was machen Sie und in welcher Stadt?\n${message || "—"}\n\n` +
      `Seite: ${page || "/"}\nZeit:  ${when}\n\n` +
      `Antworten: einfach auf diese E-Mail antworten (geht direkt an ${email}).`;

    const res = await fetch("https://api.brevo.com/v3/smtp/email", {
      method: "POST",
      headers: {
        "api-key": env.BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
      },
      body: JSON.stringify({
        sender: { email: env.FROM_EMAIL, name: "Website olhapolishchuk.de" },
        to: [{ email: env.TO_EMAIL, name: "Olha Polishchuk" }],
        replyTo: { email, name },
        subject: termin ? `[Website] Termin ${termin}: ${name} (${lang})` : `[Website] Google-Check: ${name} (${lang})`,
        textContent: text,
        tags: ["website-formular"],
      }),
    });

    if (!res.ok) {
      console.log("Brevo error", res.status, (await res.text()).slice(0, 500));
      return json({ ok: false, error: "send" }, 502, origin);
    }
    return json({ ok: true }, 200, origin);
  },
};
