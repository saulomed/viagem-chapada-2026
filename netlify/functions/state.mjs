// /api/state — estado compartilhado do site (checklist, reservas, carro).
//
// Uma Netlify Function v2 lê e grava um único documento JSON no Netlify Blobs.
// O acesso é protegido pelo gate de senha (netlify/edge-functions/gate.js),
// que roda na borda antes desta função — ninguém sem cookie válido chega aqui.
import { getStore } from '@netlify/blobs';
import { isPlainObject, mergeState } from './_state-logic.mjs';

const STORE = process.env.TRIP_STATE_STORE || 'trip-state';
const KEY = process.env.TRIP_STATE_KEY || 'chapada2026';
const MAX_BYTES = 256 * 1024;

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' }
  });
}

export default async (req) => {
  const store = getStore(STORE);

  if (req.method === 'GET' || req.method === 'HEAD') {
    const data = await store.get(KEY, { type: 'json' });
    return json({ state: data || null });
  }

  if (req.method === 'PUT' || req.method === 'POST') {
    const raw = await req.text();
    if (raw.length > MAX_BYTES) return json({ error: 'payload grande demais' }, 413);
    let body;
    try { body = JSON.parse(raw); } catch { return json({ error: 'JSON inválido' }, 400); }
    if (!isPlainObject(body)) return json({ error: 'esperado um objeto JSON' }, 400);

    const remote = await store.get(KEY, { type: 'json' });
    const merged = mergeState(remote, body);
    await store.set(KEY, JSON.stringify(merged));
    return json({ ok: true, state: merged });
  }

  return new Response('Método não permitido', {
    status: 405,
    headers: { allow: 'GET, PUT', 'cache-control': 'no-store' }
  });
};

export const config = { path: '/api/state' };
