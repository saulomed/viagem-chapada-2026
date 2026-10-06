// Lógica de mesclagem do estado do site, isolada para poder ser testada sem
// subir o Netlify. O servidor é a fonte de verdade: ele mescla o que chega
// com o que já está guardado, em vez de simplesmente sobrescrever.

export function isPlainObject(v) {
  return v !== null && typeof v === 'object' && !Array.isArray(v);
}

// Mescla por chave:
// - objetos simples (o mapa de checkboxes `_todos`) são unidos chave a chave,
//   com o que chega vencendo o conflito — mas chaves que só existem no
//   servidor (marcadas em outro aparelho) não se perdem;
// - qualquer outro tipo (arrays de reservas, etc.) segue "o que chega vence".
// `_ts` é sempre reescrito com o relógio do servidor.
export function mergeState(remote, incoming) {
  const base = isPlainObject(remote) ? remote : {};
  const out = { ...base };
  for (const [k, v] of Object.entries(isPlainObject(incoming) ? incoming : {})) {
    if (k === '_ts') continue;
    out[k] = isPlainObject(v) && isPlainObject(out[k]) ? { ...out[k], ...v } : v;
  }
  // estritamente crescente: um _ts repetido faria o cliente não detectar a
  // mudança e nunca puxar o estado novo
  out._ts = Math.max(Date.now(), (base._ts || 0) + 1);
  return out;
}
