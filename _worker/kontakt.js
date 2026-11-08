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
 */

const ALLOWED_ORIGINS = [
  "https://olhapolishchuk.de",
  "https://www.olhapolishchuk.de",
];
const LANG_LABEL = { de: "DE", uk: "UA", ru: "RU" };
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

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
    if (request.method !== "POST") return json({ ok: false, error: "method" }, 405, origin);
    if (!ALLOWED_ORIGINS.includes(origin)) return json({ ok: false, error: "origin" }, 403, origin);

    const len = Number(request.headers.get("Content-Length") || 0);
    if (len > 20000) return json({ ok: false, error: "too_large" }, 413, origin);

    let data;
    try {
      data = await request.json();
    } catch {
      return json({ ok: false, error: "bad_json" }, 400, origin);
    }

    // Ловушка для ботов: скрытое поле заполнено или форма отправлена быстрее 3 секунд →
    // отвечаем «ок», но письмо не отправляем (бот не узнает, что его отсеяли).
    if (clean(data.website, 200) || Number(data.ms) < 3000) return json({ ok: true }, 200, origin);

    const name = clean(data.name, 100).replace(/[\r\n]+/g, " ");
    const email = clean(data.email, 200);
    const message = clean(data.message, 3000);
    const lang = LANG_LABEL[data.lang] || "DE";
    const page = clean(data.page, 200);

    if (!name || !EMAIL_RE.test(email)) return json({ ok: false, error: "invalid" }, 422, origin);

    const when = new Date().toLocaleString("de-DE", { timeZone: "Europe/Berlin" });
    const text =
      `Neue Anfrage über olhapolishchuk.de (${lang})\n\n` +
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
        subject: `[Website] Google-Check: ${name} (${lang})`,
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
