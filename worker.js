// The website's only server code: it takes beta sign-ups from the form on the landing page and
// stores them in the WAITLIST database (D1). Every other request is a static file.
//
// It does not send any email. Confirmation and invitation emails are a later step.
//
//   GET /enrolled, /enrolled.csv   the sign-up list, password protected. See handleEnrolled().
//
//   POST /api/v1/waitlist   JSON body, see readSignup() below
//     200 {ok:true}                  stored
//     200 {ok:true, duplicate:true}  this email was already on the list (the first entry is kept)
//     400 {ok:false, error}          bad input
//     429 {ok:false, error}          too many attempts from one address in a minute

const MAX_BODY_BYTES = 8 * 1024;
const MAX_PER_MINUTE = 5;

const STORAGE = ["readwise", "raindrop", "instapaper", "notion", "tabs", "wechat", "other"];
const SOURCES = [
  "wechat-mp", "xiaohongshu", "zhihu", "bilibili", "jike", "weibo",
  "substack", "linkedin", "medium",
  "x", "youtube", "reddit", "hn", "github", "rss", "newsletter", "podcast", "other",
];
const ASSISTANTS = ["claude", "chatgpt", "gemini", "self-hosted-agent", "none"];
const MODES = ["own-assistant", "built-in-agent"];
const LANGS = ["zh-Hans", "en"];

const json = (status, body) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });

const text = (value, max) => (typeof value === "string" ? value.trim().slice(0, max) : "");
const oneOf = (value, allowed) => (allowed.includes(value) ? value : "");
const someOf = (value, allowed) =>
  Array.isArray(value) ? [...new Set(value.filter((v) => allowed.includes(v)))] : [];

// Turns the posted JSON into the row we store, or returns {error}.
export function readSignup(body) {
  if (!body || typeof body !== "object") return { error: "Expected a JSON object." };
  const email = text(body.email, 254).toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return { error: "Please enter a valid email address." };
  return {
    signup: {
      email,
      lang: oneOf(body.lang, LANGS) || "en",
      storage: someOf(body.storage, STORAGE),
      storage_other: text(body.storage_other, 60),
      sources: someOf(body.sources, SOURCES),
      sources_other: text(body.sources_other, 60),
      assistant: oneOf(body.assistant, ASSISTANTS),
      mode: oneOf(body.mode, MODES),
      note: text(body.note, 240),
    },
    // Filled only by bots: the field is hidden from people.
    honeypot: text(body.website, 200) !== "",
  };
}

async function sha256Hex(value) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
  return [...new Uint8Array(bytes)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function handleSignup(request, env) {
  if (request.method !== "POST") return json(405, { ok: false, error: "Use POST." });
  if (!env.WAITLIST) return json(503, { ok: false, error: "The beta list is not open yet." });

  const raw = await request.text();
  if (raw.length > MAX_BODY_BYTES) return json(400, { ok: false, error: "Request is too large." });
  let body;
  try {
    body = JSON.parse(raw);
  } catch {
    return json(400, { ok: false, error: "Expected JSON." });
  }

  const { signup, honeypot, error } = readSignup(body);
  if (error) return json(400, { ok: false, error });
  // Tell a bot it worked and store nothing.
  if (honeypot) return json(200, { ok: true });

  // The address is stored only as a hash, to slow down floods and spot repeats.
  const ipHash = await sha256Hex(request.headers.get("cf-connecting-ip") || "unknown");
  const now = new Date();
  const minuteAgo = new Date(now.getTime() - 60_000).toISOString();
  const recent = await env.WAITLIST.prepare(
    "SELECT COUNT(*) AS n FROM attempts WHERE ip_hash = ?1 AND at > ?2",
  ).bind(ipHash, minuteAgo).first();
  if (recent && recent.n >= MAX_PER_MINUTE) {
    return json(429, { ok: false, error: "Too many attempts. Please try again in a minute." });
  }
  await env.WAITLIST.prepare("INSERT INTO attempts (ip_hash, at) VALUES (?1, ?2)")
    .bind(ipHash, now.toISOString()).run();

  const result = await env.WAITLIST.prepare(
    `INSERT OR IGNORE INTO signups
       (email, lang, storage, storage_other, sources, sources_other, assistant, mode, note, ip_hash, created_at)
     VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)`,
  ).bind(
    signup.email, signup.lang,
    signup.storage.join(","), signup.storage_other,
    signup.sources.join(","), signup.sources_other,
    signup.assistant, signup.mode, signup.note,
    ipHash, now.toISOString(),
  ).run();

  const stored = result.meta && result.meta.changes > 0;
  return json(200, stored ? { ok: true } : { ok: true, duplicate: true });
}

// ---------------------------------------------------------------------------------------------
// /enrolled      the sign-up list, for the owner only
// /enrolled.csv  the same list as a spreadsheet file
//
// Protected by HTTP Basic auth. Any user name is accepted; the password is the ENROLLED_PASSWORD
// secret (`wrangler secret put ENROLLED_PASSWORD`; `.dev.vars` when running locally). It is never
// written in this file, because this repository is public.

const LABELS = {
  storage: {
    readwise: "Readwise", raindrop: "Raindrop", instapaper: "Instapaper / Pocket", notion: "Notion / Obsidian",
    tabs: "浏览器标签页", wechat: "微信文件传输助手", other: "其他",
  },
  sources: {
    "wechat-mp": "微信公众号", xiaohongshu: "小红书", zhihu: "知乎", bilibili: "B 站", jike: "即刻", weibo: "微博",
    substack: "Substack", linkedin: "LinkedIn", medium: "Medium", x: "X / Twitter", youtube: "YouTube",
    reddit: "Reddit", hn: "Hacker News", github: "GitHub", rss: "RSS", newsletter: "邮件订阅", podcast: "播客", other: "其他",
  },
  assistant: { claude: "Claude", chatgpt: "ChatGPT", gemini: "Gemini", "self-hosted-agent": "自托管 Agent", none: "暂时没有" },
  mode: { "own-assistant": "接自己的助手", "built-in-agent": "用系统自带的" },
  lang: { "zh-Hans": "中文", en: "英文" },
};

const esc = (value) =>
  String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const label = (kind, code) => LABELS[kind][code] || code;
const labels = (kind, codes, other) =>
  String(codes || "").split(",").filter(Boolean)
    .map((code) => (code === "other" && other ? `其他：${other}` : label(kind, code))).join("、");

// Compares without stopping at the first different character.
function sameText(a, b) {
  const x = new TextEncoder().encode(a);
  const y = new TextEncoder().encode(b);
  let diff = x.length ^ y.length;
  for (let i = 0; i < Math.max(x.length, y.length); i++) diff |= (x[i] || 0) ^ (y[i] || 0);
  return diff === 0;
}

function passwordFrom(request) {
  const header = request.headers.get("authorization") || "";
  if (!header.toLowerCase().startsWith("basic ")) return null;
  try {
    const decoded = new TextDecoder().decode(Uint8Array.from(atob(header.slice(6).trim()), (c) => c.charCodeAt(0)));
    return decoded.slice(decoded.indexOf(":") + 1);
  } catch {
    return null;
  }
}

const PRIVATE = { "cache-control": "no-store", "x-robots-tag": "noindex, nofollow" };

// Spreadsheet programs run a cell that starts with = + - or @ as a formula; a leading quote stops that.
const csvCell = (value) => {
  let s = String(value ?? "");
  if (/^[=+\-@]/.test(s)) s = `'${s}`;
  return `"${s.replace(/"/g, '""')}"`;
};

async function handleEnrolled(request, env, url) {
  if (!env.ENROLLED_PASSWORD) {
    return new Response("The list is not set up: the ENROLLED_PASSWORD secret is missing.\n", { status: 503, headers: PRIVATE });
  }
  const given = passwordFrom(request);
  if (given === null || !sameText(given, env.ENROLLED_PASSWORD)) {
    return new Response("Password required.\n", {
      status: 401,
      headers: { ...PRIVATE, "www-authenticate": 'Basic realm="KeepEssence enrolled", charset="UTF-8"' },
    });
  }
  if (!env.WAITLIST) return new Response("The sign-up database is not attached.\n", { status: 503, headers: PRIVATE });

  const { results: rows } = await env.WAITLIST.prepare(
    `SELECT id, email, lang, storage, storage_other, sources, sources_other, assistant, mode, note, created_at, invited_at
       FROM signups ORDER BY created_at DESC`,
  ).all();

  if (url.pathname === "/enrolled.csv") {
    const head = ["报名时间(UTC)", "邮箱", "页面", "东西堆在哪儿", "从哪里收集", "常用助手", "想用的方式", "最头疼的", "邀请时间"];
    const lines = rows.map((r) => [
      r.created_at, r.email, label("lang", r.lang), labels("storage", r.storage, r.storage_other),
      labels("sources", r.sources, r.sources_other), label("assistant", r.assistant), label("mode", r.mode), r.note, r.invited_at || "",
    ].map(csvCell).join(","));
    // The BOM makes Excel read the file as UTF-8.
    return new Response("﻿" + [head.map(csvCell).join(","), ...lines].join("\r\n") + "\r\n", {
      headers: { ...PRIVATE, "content-type": "text/csv; charset=utf-8", "content-disposition": 'attachment; filename="keepessence-enrolled.csv"' },
    });
  }

  const count = (test) => rows.filter(test).length;
  const body = rows.map((r) => `
      <tr data-lang="${esc(r.lang)}">
        <td class="mono">${esc(String(r.created_at).replace("T", " ").slice(0, 16))}</td>
        <td><a href="mailto:${esc(r.email)}">${esc(r.email)}</a></td>
        <td>${esc(label("lang", r.lang))}</td>
        <td>${esc(labels("storage", r.storage, r.storage_other))}</td>
        <td>${esc(labels("sources", r.sources, r.sources_other))}</td>
        <td>${esc(label("assistant", r.assistant))}</td>
        <td>${esc(label("mode", r.mode))}</td>
        <td>${esc(r.note)}</td>
      </tr>`).join("");

  const html = `<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>内测报名名单 · KeepEssence</title>
  <style>
    :root { color-scheme: dark; }
    body { margin: 0; padding: 24px; background: #0B0B0B; color: #F4F4F2; font: 14px/1.5 -apple-system, BlinkMacSystemFont, "PingFang SC", "Noto Sans SC", sans-serif; }
    h1 { margin: 0 0 4px; font-size: 20px; }
    .sum { color: #B6B6B1; margin: 0 0 16px; }
    .bar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 14px; }
    .bar button, .bar a { font: inherit; padding: 6px 12px; border-radius: 6px; border: 1px solid #3E3E3A; background: #141414; color: #F4F4F2; text-decoration: none; cursor: pointer; }
    .bar button[aria-pressed="true"] { background: #F4F4F2; color: #0B0B0B; border-color: #F4F4F2; }
    .bar input { font: inherit; padding: 6px 10px; border-radius: 6px; border: 1px solid #3E3E3A; background: #0B0B0B; color: #F4F4F2; min-width: 200px; }
    .wrap { overflow-x: auto; border: 1px solid #2A2A28; border-radius: 10px; }
    table { border-collapse: collapse; width: 100%; min-width: 980px; }
    th, td { text-align: left; vertical-align: top; padding: 9px 12px; border-bottom: 1px solid #222220; }
    th { position: sticky; top: 0; background: #141414; color: #B6B6B1; font-weight: 500; font-size: 12.5px; white-space: nowrap; }
    tr:last-child td { border-bottom: 0; }
    td a { color: #F4F4F2; }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; color: #B6B6B1; white-space: nowrap; }
    .empty { padding: 28px; color: #858580; }
  </style>
</head>
<body>
  <h1>内测报名名单</h1>
  <p class="sum">共 ${rows.length} 人 · 中文页 ${count((r) => r.lang === "zh-Hans")} · 英文页 ${count((r) => r.lang === "en")} · 想接自己的助手 ${count((r) => r.mode === "own-assistant")} · 想用系统自带的 ${count((r) => r.mode === "built-in-agent")}。时间是 UTC。</p>
  <div class="bar">
    <button type="button" data-f="" aria-pressed="true">全部</button>
    <button type="button" data-f="zh-Hans" aria-pressed="false">中文页</button>
    <button type="button" data-f="en" aria-pressed="false">英文页</button>
    <input type="search" placeholder="搜邮箱或任意文字" aria-label="搜索名单">
    <a href="/enrolled.csv">下载表格（CSV）</a>
  </div>
  <div class="wrap">
    ${rows.length ? `<table>
      <thead><tr><th>报名时间</th><th>邮箱</th><th>页面</th><th>东西堆在哪儿</th><th>从哪里收集</th><th>常用助手</th><th>想用的方式</th><th>最头疼的</th></tr></thead>
      <tbody>${body}
      </tbody>
    </table>` : '<div class="empty">还没有人报名。</div>'}
  </div>
  <script>
    (() => {
      const rows = Array.from(document.querySelectorAll("tbody tr"));
      const buttons = Array.from(document.querySelectorAll("[data-f]"));
      const box = document.querySelector("input[type=search]");
      let lang = "";
      const apply = () => {
        const q = box.value.trim().toLowerCase();
        rows.forEach((tr) => { tr.hidden = (lang && tr.dataset.lang !== lang) || (q && !tr.textContent.toLowerCase().includes(q)); });
      };
      buttons.forEach((b) => b.addEventListener("click", () => {
        lang = b.dataset.f;
        buttons.forEach((x) => x.setAttribute("aria-pressed", String(x === b)));
        apply();
      }));
      box.addEventListener("input", apply);
    })();
  </script>
</body>
</html>`;
  return new Response(html, { headers: { ...PRIVATE, "content-type": "text/html; charset=utf-8" } });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/enrolled" || url.pathname === "/enrolled/" || url.pathname === "/enrolled.csv") {
      try {
        return await handleEnrolled(request, env, url);
      } catch (err) {
        console.error("enrolled list failed", err);
        return new Response("Something went wrong.\n", { status: 500, headers: PRIVATE });
      }
    }
    if (url.pathname === "/api/v1/waitlist") {
      try {
        return await handleSignup(request, env);
      } catch (err) {
        console.error("waitlist signup failed", err);
        return json(500, { ok: false, error: "Something went wrong. Please try again later." });
      }
    }
    if (url.pathname.startsWith("/api/")) return json(404, { ok: false, error: "Not found." });
    return env.ASSETS.fetch(request);
  },
};
