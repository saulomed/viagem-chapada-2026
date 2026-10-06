// site-sync.js — estado compartilhado do site via função do próprio Netlify.
//
// Substitui o gist-sync.js quando `features.siteSync` está ligado: expõe a
// MESMA interface `window.GistSync` que o app.js já consome, mas o "banco" é
// o endpoint /api/state do site (Netlify Function + Blobs) em vez de um Gist.
// Vantagem: ninguém precisa colar token — o login é a própria senha do site,
// e o gate de borda protege o endpoint junto com o resto do conteúdo.
//
// Configurado por window.TRIP_SYNC = { prefix, endpoint, keys }, injetado pelo build.
(function () {
  'use strict';

  var CFG = window.TRIP_SYNC || {};
  var PREFIX = CFG.prefix || 'trip';
  var ENDPOINT = CFG.endpoint || '/api/state';
  var SYNC_KEYS = CFG.keys || [PREFIX + '_todos', PREFIX + '_bookings', PREFIX + '_car_booking'];
  // Guarda o _ts do último estado do servidor que este aparelho viu. É o que
  // decide se há algo mais novo para puxar — comparar com um _ts local
  // (sempre "agora") nunca puxaria nada.
  var TS_KEY = PREFIX + '_synced_ts';

  var status = 'idle';
  var statusCallbacks = [];
  var saveTimer = null;

  function setStatus(s) { status = s; statusCallbacks.forEach(function (cb) { cb(s); }); }
  function onStatusChange(cb) { statusCallbacks.push(cb); cb(status); }
  function getStatus() { return status; }

  // O servidor cuida de quem pode entrar (gate de senha). Para o app.js,
  // o sync está sempre "configurado".
  function isConfigured() { return true; }

  function getLastTs() {
    var raw = localStorage.getItem(TS_KEY);
    return raw ? (parseInt(raw, 10) || 0) : 0;
  }
  function setLastTs(ts) { if (ts) localStorage.setItem(TS_KEY, String(ts)); }

  function getLocalState() {
    var state = {};
    SYNC_KEYS.forEach(function (key) {
      var raw = localStorage.getItem(key);
      if (raw !== null) { try { state[key] = JSON.parse(raw); } catch (e) {} }
    });
    return state;
  }

  function hasLocalData() {
    return SYNC_KEYS.some(function (key) { return localStorage.getItem(key) !== null; });
  }

  function applyState(state) {
    if (!state) return;
    SYNC_KEYS.forEach(function (key) {
      if (state[key] !== undefined) localStorage.setItem(key, JSON.stringify(state[key]));
    });
  }

  function getRemote() {
    return fetch(ENDPOINT, {
      headers: { Accept: 'application/json' },
      credentials: 'same-origin',
      cache: 'no-store'
    }).then(function (r) {
      if (r.status === 401) throw new Error('não autenticado');
      if (!r.ok) throw new Error('GET ' + r.status);
      return r.json();
    }).then(function (data) {
      if (!data) return null;
      if (data.state !== undefined) return data.state;
      return data._ts !== undefined ? data : null;
    });
  }

  function putRemote(state) {
    return fetch(ENDPOINT, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      body: JSON.stringify(state)
    }).then(function (r) {
      if (r.status === 401) throw new Error('não autenticado');
      if (!r.ok) throw new Error('PUT ' + r.status);
      return r.json().catch(function () { return {}; });
    });
  }

  function syncOnLoad() {
    setStatus('syncing');
    return getRemote().then(function (remote) {
      // primeira vez neste aparelho e servidor vazio: manda o que é local
      if (!remote) {
        if (!hasLocalData()) { setStatus('synced'); return false; }
        return saveNow().then(function () { return true; });
      }
      if ((remote._ts || 0) > getLastTs()) {
        applyState(remote);
        setLastTs(remote._ts);
        setStatus('synced');
        return true;
      }
      setStatus('synced');
      return false;
    }).catch(function (e) {
      console.warn('[sync]', e.message);
      setStatus('error');
      return false;
    });
  }

  function saveNow() {
    setStatus('syncing');
    return putRemote(getLocalState()).then(function (resp) {
      // o servidor devolve o estado já mesclado; reflete o que de fato ficou
      if (resp && resp.state) {
        applyState(resp.state);
        setLastTs(resp.state._ts);
      }
      setStatus('synced');
    }).catch(function (e) {
      console.warn('[sync]', e.message);
      setStatus('error');
    });
  }

  function debouncedSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(saveNow, 1500);
  }

  var api = {
    isConfigured: isConfigured,
    syncOnLoad: syncOnLoad,
    saveNow: saveNow,
    debouncedSave: debouncedSave,
    onStatusChange: onStatusChange,
    getStatus: getStatus,
    testConnection: function () {
      return getRemote().then(function () { return true; }).catch(function () { return false; });
    },
    // sem credenciais para guardar: existem só para bater com a interface do app.js
    saveCredentials: function () {},
    clearCredentials: function () { setStatus('idle'); }
  };

  window.GistSync = api;
  window.SiteSync = api;
})();
