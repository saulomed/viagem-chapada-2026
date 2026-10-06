// Gate de senha única do site — roda na borda, antes de qualquer byte sair.
//
// Sem cookie assinado válido, nada é servido: nem HTML, nem imagem, nem o
// endpoint /api/state. A senha vive só numa variável de ambiente do Netlify
// (SITE_PASSWORD) e nunca chega ao navegador. O cookie é um par
// `expiração.assinatura` (HMAC-SHA256 com SESSION_SECRET), HttpOnly.
//
// Variáveis de ambiente obrigatórias no Netlify:
//   SITE_PASSWORD   senha única do grupo
//   SESSION_SECRET  string aleatória longa para assinar o cookie
// Sem as duas, o portão fica aberto (útil em desenvolvimento local).

const COOKIE = 'site_auth';
const MAX_AGE = 60 * 60 * 24 * 30; // 30 dias
const encoder = new TextEncoder();

function b64url(bytes) {
  const arr = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let s = '';
  for (let i = 0; i < arr.length; i++) s += String.fromCharCode(arr[i]);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function sign(value, secret) {
  const key = await crypto.subtle.importKey(
    'raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
  );
  return b64url(await crypto.subtle.sign('HMAC', key, encoder.encode(value)));
}

// comparação em tempo constante — evita descobrir a senha pelo tempo de resposta
function timingSafeEqual(a, b) {
  const x = encoder.encode(String(a));
  const y = encoder.encode(String(b));
  if (x.length !== y.length) return false;
  let diff = 0;
  for (let i = 0; i < x.length; i++) diff |= x[i] ^ y[i];
  return diff === 0;
}

function parseCookies(header) {
  const out = {};
  (header || '').split(';').forEach((part) => {
    const i = part.indexOf('=');
    if (i > -1) out[part.slice(0, i).trim()] = part.slice(i + 1).trim();
  });
  return out;
}

async function makeToken(secret) {
  const exp = Math.floor(Date.now() / 1000) + MAX_AGE;
  return `${exp}.${await sign(String(exp), secret)}`;
}

async function isValidToken(token, secret) {
  if (!token) return false;
  const i = token.indexOf('.');
  if (i < 1) return false;
  const exp = token.slice(0, i);
  const sig = token.slice(i + 1);
  if (!/^\d+$/.test(exp) || Number(exp) < Math.floor(Date.now() / 1000)) return false;
  return timingSafeEqual(sig, await sign(exp, secret));
}

function cookieHeader(token, secure) {
  return `${COOKIE}=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=${MAX_AGE}` +
    (secure ? '; Secure' : '');
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// só aceita caminho interno: evita virar trampolim para outro site
function safeRedirect(r) {
  return typeof r === 'string' && r.startsWith('/') && !r.startsWith('//') ? r : '/';
}

function loginPage({ error = '', redirect = '/', title = 'Viagem' } = {}) {
  return `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>Entrar · ${esc(title)}</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body {
    margin: 0; min-height: 100svh; display: grid; place-items: center;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #4a3227; color: #f7f1ea;
  }
  .card {
    width: min(92vw, 360px); background: #5d4133; border: 1px solid rgba(255,255,255,.12);
    border-radius: 16px; padding: 1.8rem 1.6rem; box-shadow: 0 18px 50px rgba(0,0,0,.35);
  }
  .emoji { font-size: 2rem; }
  h1 { font-size: 1.2rem; margin: .5rem 0 .2rem; }
  p.sub { margin: 0 0 1.2rem; font-size: .85rem; opacity: .75; }
  label { display: block; font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; opacity: .8; margin-bottom: .35rem; }
  input[type=password] {
    width: 100%; padding: .7rem .8rem; border-radius: 10px; font-size: 1rem;
    border: 1px solid rgba(255,255,255,.2); background: rgba(0,0,0,.2); color: inherit;
  }
  button {
    width: 100%; margin-top: 1rem; padding: .75rem; border: 0; border-radius: 10px;
    font-size: .95rem; font-weight: 700; cursor: pointer;
    background: #e0954f; color: #3a271c;
  }
  button:hover { filter: brightness(1.05); }
  .err { margin-top: .8rem; font-size: .85rem; color: #ffb4a2; }
</style>
</head>
<body>
  <form class="card" method="POST" action="/__auth">
    <div class="emoji">🔒</div>
    <h1>Roteiro protegido</h1>
    <p class="sub">Digite a senha do grupo para continuar.</p>
    <label for="password">Senha</label>
    <input id="password" name="password" type="password" autocomplete="current-password" autofocus required>
    <input type="hidden" name="redirect" value="${esc(safeRedirect(redirect))}">
    <button type="submit">Entrar</button>
    ${error ? `<div class="err">${esc(error)}</div>` : ''}
  </form>
</body>
</html>`;
}

function htmlResponse(body, status) {
  return new Response(body, {
    status,
    headers: { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' }
  });
}

export default async function gate(req, context) {
  const password = Netlify.env.get('SITE_PASSWORD') || '';
  const secret = Netlify.env.get('SESSION_SECRET') || '';
  const url = new URL(req.url);

  // Portão aberto quando não configurado (dev local / primeiro deploy)
  if (!password || !secret) return context.next();

  // Endpoints internos do Netlify nunca passam pelo portão
  if (url.pathname.startsWith('/.netlify/')) return context.next();

  const secure = url.protocol === 'https:';
  const cookies = parseCookies(req.headers.get('cookie'));

  if (url.pathname === '/__auth') {
    if (req.method !== 'POST') return htmlResponse(loginPage(), 405);
    const form = await req.formData();
    const given = String(form.get('password') || '');
    const redirect = safeRedirect(String(form.get('redirect') || '/'));
    if (timingSafeEqual(given, password)) {
      return new Response(null, {
        status: 303,
        headers: { location: redirect, 'set-cookie': cookieHeader(await makeToken(secret), secure) }
      });
    }
    // atrasa tentativas erradas; não consome CPU da borda (só espera)
    await new Promise((r) => setTimeout(r, 700));
    return htmlResponse(loginPage({ error: 'Senha incorreta. Tente de novo.', redirect }), 401);
  }

  if (url.pathname === '/__logout') {
    return new Response(null, {
      status: 303,
      headers: {
        location: '/',
        'set-cookie': `${COOKIE}=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0` + (secure ? '; Secure' : '')
      }
    });
  }

  if (await isValidToken(cookies[COOKIE], secret)) return context.next();

  const accept = req.headers.get('accept') || '';
  if (req.method === 'GET' && accept.includes('text/html')) {
    return htmlResponse(loginPage({ redirect: url.pathname + url.search }), 401);
  }
  return new Response('Não autorizado', {
    status: 401,
    headers: { 'content-type': 'text/plain; charset=utf-8', 'cache-control': 'no-store' }
  });
}

export const config = { path: '/*' };
