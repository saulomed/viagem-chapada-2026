// app.js — lógica compartilhada do roteiro. Cada módulo só roda se seus elementos existem.
// Dados vêm de window.TRIP_DATA, injetado pelo build.
(function () {
  'use strict';

  var D = window.TRIP_DATA || {};
  var META = D.meta || {};
  var P = META.storagePrefix || 'trip';
  var K = { todos: P + '_todos', bookings: P + '_bookings', car: P + '_car_booking' };

  var WEEKDAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

  // ═══════════ helpers ═══════════
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); }
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }
  function readJSON(key, fallback) {
    try { return JSON.parse(localStorage.getItem(key)) || fallback; } catch (e) { return fallback; }
  }
  function writeJSON(key, val) {
    localStorage.setItem(key, JSON.stringify(val));
    if (window.GistSync && window.GistSync.isConfigured()) window.GistSync.debouncedSave();
  }
  function parseISO(iso) { var p = String(iso).split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function fmtBR(iso) { var p = String(iso).split('-'); return p[2] + '/' + p[1]; }
  function weekday(iso) { return WEEKDAYS[parseISO(iso).getDay()]; }
  function reconvert(root) { if (window.applyConversion) window.applyConversion(root); }
  function esc(t) {
    return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // ═══════════ procedência de um número ═══════════
  // Espelha fato_html() do build.py: um preço pode ser string (como sempre) ou
  // { text, status, source }. O selo separa preço oficial de estimativa.
  var STATUS_SELO = {
    confirmado: ['✅', 'Confirmado — já reservado ou pago'],
    cotado: ['🔎', 'Cotado — preço verificado na fonte oficial'],
    estimado: ['⚠️', 'Estimado — sem fonte oficial, confirme antes de contar com o valor']
  };

  function fatoHTML(v) {
    if (v == null) return '';
    if (typeof v !== 'object') return esc(v);
    var txt = esc(v.text || '');
    var selo = STATUS_SELO[v.status];
    if (!selo) return txt;
    var src = (D.sources || {})[v.source || ''];
    var titulo = selo[1];
    if (src) {
      titulo += ' · ' + (src.label || '');
      // data de consulta precisa do ano: fmtBR() corta para DD/MM
      if (src.consultadoEm) {
        var pd = String(src.consultadoEm).split('-');
        titulo += ' (consultado em ' + pd[2] + '/' + pd[1] + '/' + pd[0] + ')';
      }
      if (src.url) {
        return txt + ' <a class="fato-selo st-' + v.status + '" href="' + esc(src.url) +
               '" target="_blank" rel="noopener" title="' + esc(titulo) + '">' + selo[0] + '</a>';
      }
    }
    return txt + ' <span class="fato-selo st-' + v.status + '" title="' + esc(titulo) + '">' +
           selo[0] + '</span>';
  }

  // ═══════════ fade-in ═══════════
  // .fade-in nasce com opacity 0 e só aparece ao ganhar .visible. Observar
  // apenas o que existe no load deixa invisível todo card criado depois — ou
  // reexibido depois de um filtro. O MutationObserver fecha esse buraco, e
  // window.revelar() serve para quem precisa exibir na hora, sem esperar rolagem.
  var fadeIO = null;

  function observarFade(raiz) {
    if (!fadeIO) return;
    var alvos = (raiz && raiz.classList && raiz.classList.contains('fade-in')) ? [raiz] : [];
    alvos = alvos.concat($$('.fade-in', raiz || document));
    alvos.forEach(function (e) { if (!e.classList.contains('visible')) fadeIO.observe(e); });
  }

  // Exibe imediatamente, sem depender de rolagem. Use depois de filtrar,
  // reordenar ou inserir cards por JS.
  window.revelar = function (raiz) {
    var alvos = (raiz && raiz.classList && raiz.classList.contains('fade-in')) ? [raiz] : [];
    alvos = alvos.concat($$('.fade-in', raiz || document));
    alvos.forEach(function (e) { e.classList.add('visible'); });
  };

  function initFadeIn() {
    if (!window.IntersectionObserver) { window.revelar(document); return; }
    fadeIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('visible'); fadeIO.unobserve(e.target); }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    observarFade(document);

    if (window.MutationObserver) {
      new MutationObserver(function (muts) {
        muts.forEach(function (m) {
          Array.prototype.forEach.call(m.addedNodes, function (n) {
            if (n.nodeType === 1) observarFade(n);
          });
        });
      }).observe(document.body, { childList: true, subtree: true });
    }
  }

  // ═══════════ navegação ═══════════
  window.navigateTo = function (selector) {
    var target = $(selector);
    if (!target) return;
    var nav = $('#navbar');
    var offset = (nav ? nav.offsetHeight : 0) + 10;
    window.scrollTo({ top: target.getBoundingClientRect().top + window.pageYOffset - offset, behavior: 'smooth' });
  };

  function initNavSpy() {
    var btns = $$('.nav-btn[data-section]');
    if (!btns.length) return;
    var nav = $('#navbar');
    window.addEventListener('scroll', function () {
      var offset = (nav ? nav.offsetHeight : 0) + 24;
      var current = '';
      btns.forEach(function (b) {
        var sec = document.getElementById(b.dataset.section);
        if (sec && sec.getBoundingClientRect().top <= offset) current = b.dataset.section;
      });
      btns.forEach(function (b) { b.classList.toggle('active', b.dataset.section === current); });
    }, { passive: true });
  }

  // ═══════════ reservas de hospedagem ═══════════
  function getBookings() {
    var raw = readJSON(K.bookings, {});
    var out = {};
    Object.keys(raw).forEach(function (loc) {
      out[loc] = Array.isArray(raw[loc]) ? raw[loc] : [raw[loc]];
    });
    return out;
  }

  function findBookingForDay(day, bookings) {
    var arr = (bookings[day.location] || []);
    var hit = arr.find(function (b) {
      if (!b.checkin || !b.checkout) return true;
      return day.date >= b.checkin && day.date < b.checkout;
    });
    if (hit) return hit;
    var loc = (D.lodging && D.lodging.locations || []).find(function (l) { return l.id === day.location; });
    if (!loc) return null;
    var reserved = (loc.options || []).find(function (o) { return o.reserved; });
    return reserved ? Object.assign({ _fromData: true }, reserved) : null;
  }

  // ═══════════ calendário + detalhe do dia ═══════════
  function initCalendar() {
    var grid = $('#calendarGrid');
    var detail = $('#dayDetail');
    if (!grid || !detail || !D.days) return;

    var current = 0, first = true;

    D.days.forEach(function (d, i) {
      var c = el('div', 'cal-day');
      c.innerHTML =
        '<div class="cal-wd">' + weekday(d.date) + '</div>' +
        '<div class="cal-num">' + fmtBR(d.date) + '</div>' +
        '<div class="cal-emoji">' + (d.emoji || '📍') + '</div>' +
        '<div class="cal-city">' + d.city + '</div>';
      c.addEventListener('click', function () { select(i); });
      grid.appendChild(c);
    });

    function select(i) {
      current = i;
      $$('.cal-day', grid).forEach(function (c, j) { c.classList.toggle('active', i === j); });
      render(D.days[i]);
      if (!first) {
        setTimeout(function () { window.navigateTo('#dayDetail'); }, 60);
      }
      first = false;
    }

    // ①②③… gerados pelo site. Numerar à mão dentro do texto foi o que já
    // produziu dois "⑤" no mesmo bloco sem ninguém perceber.
    var CIRCULOS = '①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮';
    var PET_SELO = {
      sim: ['pet-sim', '🐕 pode ir'],
      nao: ['pet-nao', '🚫 sem pet'],
      confirmar: ['pet-talvez', '🐕 a confirmar']
    };
    var TEM_PET = !!((META.profile || {}).pets || []).length;

    function renderOption(o, i) {
      var selo = TEM_PET && o.pet && PET_SELO[o.pet];
      return '<li class="day-option">' +
        '<span class="opt-num">' + (CIRCULOS.charAt(i) || (i + 1) + '.') + '</span>' +
        '<span class="opt-body">' +
          (selo ? '<span class="opt-pet ' + selo[0] + '">' + selo[1] + '</span>' : '') +
          '<strong>' + o.title + '</strong>' +
          (o.text ? ' — ' + o.text : '') +
          (o.price ? '<span class="opt-price">' + fatoHTML(o.price) + '</span>' : '') +
        '</span>' +
      '</li>';
    }

    function renderBlock(b) {
      var links = [];
      if (b.maps) links.push('<a href="' + b.maps + '" target="_blank" rel="noopener">📍 Google Maps</a>');
      if (b.waze) links.push('<a href="' + b.waze + '" target="_blank" rel="noopener">🧭 Waze</a>');

      var opcoes = (b.options || []).length
        ? '<ol class="day-options">' + b.options.map(renderOption).join('') + '</ol>'
        : '';

      return '<div class="block">' +
        '<div class="block-time">' + b.time + '</div>' +
        '<div>' +
          '<div class="block-title">' + b.title +
            (b.tip ? '<span class="block-tip">' + b.tip + '</span>' : '') +
          '</div>' +
          '<ul class="block-items">' + (b.items || []).map(function (it) { return '<li>' + it + '</li>'; }).join('') + '</ul>' +
          opcoes +
          (b.duration ? '<div class="block-duration">⏱ ' + fatoHTML(b.duration) + '</div>' : '') +
          (links.length ? '<div class="block-links">' + links.join('') + '</div>' : '') +
          (b.price ? '<div class="price-tag">' + fatoHTML(b.price) + '</div>' : '') +
        '</div>' +
      '</div>';
    }

    function render(d) {
      var bookings = getBookings();
      var stay = findBookingForDay(d, bookings);
      var loc = (D.lodging && D.lodging.locations || []).find(function (l) { return l.id === d.location; });

      var stayHTML = '';
      if (stay) {
        var confirmations = (stay.confirmationUrls || []).map(function (c) {
          return '<a href="' + c.url + '" target="_blank" rel="noopener">📄 ' + c.label + '</a>';
        }).join('');
        stayHTML =
          '<div class="hotel-card reserved" style="margin-top:24px">' +
            '<span class="hotel-badge">✅ Reservado</span>' +
            '<h4>🏨 ' + stay.name + '</h4>' +
            (stay.desc ? '<div class="desc">' + stay.desc + '</div>' : '') +
            (stay.price ? '<div class="hotel-price">' + stay.price + '</div>' : '') +
            (stay.checkin ? '<div class="block-duration">' + fmtBR(stay.checkin) + ' → ' + fmtBR(stay.checkout) + '</div>' : '') +
            (confirmations ? '<div class="block-links">' + confirmations + '</div>' : '') +
          '</div>';
      } else if (loc) {
        stayHTML = '<div style="margin-top:24px"><a class="btn ghost" href="hospedagem.html#' + loc.id + '">Ver opções de hospedagem em ' + loc.name + ' →</a></div>';
      }

      detail.innerHTML =
        '<div class="day-head">' +
          '<div class="num">Dia ' + d.num + ' · ' + weekday(d.date) + ' ' + fmtBR(d.date) + '</div>' +
          '<h3>' + (d.emoji || '') + ' ' + d.title + '</h3>' +
          (d.route ? '<div class="route">' + d.route + '</div>' : '') +
        '</div>' +
        '<div class="day-body">' + (d.blocks || []).map(renderBlock).join('') + stayHTML + '</div>';

      reconvert(detail);
    }

    select(0);
    window.addEventListener('fx-ready', function () { render(D.days[current]); });
    window.addEventListener('storage', function (e) {
      if (e.key === K.bookings) render(D.days[current]);
    });
  }

  // ═══════════ checklist ═══════════
  function initTodos() {
    var grid = $('#todoGrid');
    if (!grid || !D.todos) return;

    function autoState(item) {
      if (item.autoType === 'car') {
        var car = readJSON(K.car, null);
        return car ? { label: 'Reserva salva' + (car.confirmation ? ' · ' + car.confirmation : '') } : null;
      }
      if (item.autoType === 'booking' && item.autoKey) {
        var arr = getBookings()[item.autoKey] || [];
        var hit = item.autoDate
          ? arr.find(function (b) { return !b.checkin || (item.autoDate >= b.checkin && item.autoDate < b.checkout); })
          : arr[0];
        return hit ? { label: hit.name + (hit.checkin ? ' · ' + fmtBR(hit.checkin) : '') } : null;
      }
      return null;
    }

    function render() {
      var todos = readJSON(K.todos, {});
      var total = 0, done = 0;
      grid.innerHTML = '';

      D.todos.forEach(function (group) {
        var groupDone = 0;
        var items = (group.items || []).map(function (item) {
          var auto = autoState(item);
          var isDone = !!auto || todos[item.id] === true;
          total++;
          if (isDone) { done++; groupDone++; }
          return '<div class="todo-item' + (isDone ? ' done' : '') + (auto ? ' auto' : '') + '" data-id="' + item.id + '"' +
              (auto ? '' : ' role="button" tabindex="0"') + '>' +
              '<span class="box">' + (isDone ? '✓' : '') + '</span>' +
              '<span class="txt">' + item.text + '</span>' +
            '</div>' +
            (auto ? '<div class="todo-auto-label">🔗 ' + auto.label + '</div>' : '');
        }).join('');

        var card = el('div', 'todo-card fade-in' + (groupDone === (group.items || []).length ? ' done' : ''));
        card.innerHTML =
          '<h3>' + (group.emoji || '') + ' ' + group.city + '</h3>' +
          (group.subtitle ? '<div class="sub">' + group.subtitle + '</div>' : '') +
          items;
        grid.appendChild(card);
        card.classList.add('visible');
      });

      var pct = total ? Math.round(done / total * 100) : 0;
      var bar = $('#todoBar'), lbl = $('#todoPct');
      if (bar) bar.style.width = pct + '%';
      if (lbl) lbl.textContent = done + '/' + total + ' · ' + pct + '%';
    }

    grid.addEventListener('click', function (e) {
      var item = e.target.closest('.todo-item');
      if (!item || item.classList.contains('auto')) return;
      var todos = readJSON(K.todos, {});
      todos[item.dataset.id] = !todos[item.dataset.id];
      writeJSON(K.todos, todos);
      render();
    });

    render();
    window.addEventListener('storage', function (e) {
      if (e.key === K.todos || e.key === K.bookings) render();
    });
    window.__renderTodos = render;
  }

  // ═══════════ resumo de custos ═══════════
  function initCostSummary() {
    var grid = $('#summaryGrid');
    if (!grid || !D.costs) return;
    (D.costs.categories || []).forEach(function (c) {
      var card = el('div', 'cost-card fade-in');
      card.innerHTML = '<div class="label">' + (c.emoji || '') + ' ' + c.title + '</div>' +
                       '<span class="amount">' + c.totalLabel + '</span>';
      grid.appendChild(card);
    });
    var total = el('div', 'cost-card total fade-in');
    total.innerHTML = '<div class="label">Total estimado</div><span class="amount">' + D.costs.totalLabel + '</span>';
    grid.appendChild(total);
    reconvert(grid);
  }

  // ═══════════ conversor de moeda ═══════════
  function initConverter() {
    var dsp = $('#conv-display');
    if (!dsp) return;
    var home = $('#conv-home'), local = $('#conv-local'), rates = $('#conv-rates');
    var busy = false;

    function num(v) { return parseFloat(String(v).replace(/\./g, '').replace(',', '.')) || 0; }
    function show(v) { return v ? v.toLocaleString('pt-BR', { maximumFractionDigits: 2 }) : ''; }

    function sync(source) {
      if (busy || !window.TRIP_RATE) return;
      busy = true;
      var base = source === 'display' ? num(dsp.value)
        : source === 'home' ? num(home.value) / window.TRIP_RATE
        : num(local.value) / (window.LOCAL_RATE || 1);
      if (source !== 'display') dsp.value = show(base);
      if (source !== 'home' && home) home.value = show(base * window.TRIP_RATE);
      if (source !== 'local' && local && window.LOCAL_RATE) local.value = show(base * window.LOCAL_RATE);
      busy = false;
    }

    dsp.addEventListener('input', function () { sync('display'); });
    if (home) home.addEventListener('input', function () { sync('home'); });
    if (local) local.addEventListener('input', function () { sync('local'); });

    window.addEventListener('fx-ready', function () {
      if (rates) {
        rates.textContent = '1 ' + META.currency.display + ' = ' + window.TRIP_RATE.toFixed(3) + ' ' + META.currency.home +
          (window.LOCAL_RATE ? '  ·  1 ' + META.currency.display + ' = ' + window.LOCAL_RATE.toFixed(2) + ' ' + META.currency.local : '');
      }
      dsp.value = '100';
      sync('display');
    });
  }

  // ═══════════ hospedagem: marcar reserva ═══════════
  function initLodging() {
    var root = $('#lodgingRoot');
    if (!root) return;
    var pending = null;

    function refresh() {
      var bookings = getBookings();
      $$('.hotel-card[data-hotel]', root).forEach(function (card) {
        var loc = card.dataset.location;
        var name = card.dataset.name;
        var hit = (bookings[loc] || []).find(function (b) { return b.name === name; });
        var preset = card.dataset.reserved === 'true';
        card.classList.toggle('reserved', !!hit || preset);
        var btn = $('.js-book', card);
        if (btn) {
          btn.textContent = hit ? 'Cancelar reserva' : (preset ? 'Confirmar datas' : 'Marcar como reservado');
          btn.classList.toggle('danger', !!hit);
        }
        var info = $('.js-booking-info', card);
        if (info) {
          info.innerHTML = hit && hit.checkin
            ? '<div class="block-duration">' + fmtBR(hit.checkin) + ' → ' + fmtBR(hit.checkout) +
              (hit.cancelDate ? ' · cancelamento grátis até ' + fmtBR(hit.cancelDate) : '') +
              (hit.pin ? ' · cód. ' + hit.pin : '') + '</div>'
            : '';
        }
      });
      if (window.__renderTodos) window.__renderTodos();
    }

    root.addEventListener('click', function (e) {
      var btn = e.target.closest('.js-book');
      if (!btn) return;
      var card = btn.closest('.hotel-card');
      var loc = card.dataset.location, name = card.dataset.name;
      var bookings = getBookings();
      var arr = bookings[loc] || [];
      var idx = arr.findIndex(function (b) { return b.name === name; });

      if (idx >= 0) {
        arr.splice(idx, 1);
        bookings[loc] = arr;
        writeJSON(K.bookings, bookings);
        refresh();
        return;
      }
      pending = { card: card, location: loc, name: name };
      openModal(loc, name);
    });

    function openModal(loc, name) {
      var overlay = $('#bookingModal');
      $('#bookingHotelName').textContent = name;
      $('#bookingError').textContent = '';
      var location = (D.lodging.locations || []).find(function (l) { return l.id === loc; });
      var chips = $('#bookingChips');
      chips.innerHTML = '';
      ((location && location.dates) || []).forEach(function (d, i) {
        var chip = el('button', 'date-chip', (d.label || fmtBR(d.checkin) + ' → ' + fmtBR(d.checkout)));
        chip.type = 'button';
        chip.addEventListener('click', function () {
          $$('.date-chip', chips).forEach(function (c) { c.classList.remove('active'); });
          chip.classList.add('active');
          $('#bookingCheckin').value = d.checkin;
          $('#bookingCheckout').value = d.checkout;
        });
        chips.appendChild(chip);
        if (i === 0) chip.click();
      });
      overlay.classList.add('open');
    }

    window.closeBookingModal = function (e) {
      if (e && e.target !== e.currentTarget) return;
      $('#bookingModal').classList.remove('open');
      pending = null;
    };

    window.confirmBooking = function () {
      if (!pending) return;
      var checkin = $('#bookingCheckin').value, checkout = $('#bookingCheckout').value;
      var err = $('#bookingError');
      if (!checkin || !checkout) { err.textContent = 'Informe check-in e check-out.'; return; }
      if (checkout <= checkin) { err.textContent = 'Check-out precisa ser depois do check-in.'; return; }

      var bookings = getBookings();
      var arr = bookings[pending.location] || [];
      arr.push({
        name: pending.name,
        checkin: checkin,
        checkout: checkout,
        pin: $('#bookingPin').value.trim() || null,
        cancelDate: $('#bookingCancel').value || null,
        ts: Date.now()
      });
      bookings[pending.location] = arr;
      writeJSON(K.bookings, bookings);
      $('#bookingModal').classList.remove('open');
      pending = null;
      refresh();
    };

    refresh();
    window.addEventListener('storage', function (e) { if (e.key === K.bookings) refresh(); });
  }

  // ═══════════ mapa ═══════════
  function initMap() {
    if (!$('#map') || typeof L === 'undefined' || !D.stops || !D.stops.length) return;

    var COLORS = { city: '#4fc3f7', nature: '#66bb6a', beach: '#ffb74d', mountain: '#9575cd', default: '#e85d3a' };
    var stops = D.stops;
    var map = L.map('map', { scrollWheelZoom: true, zoomControl: true });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap', maxZoom: 18
    }).addTo(map);

    var coords = stops.map(function (s) { return [s.lat, s.lng]; });
    L.polyline(coords, { color: '#fff', weight: 7, opacity: 0.6 }).addTo(map);
    L.polyline(coords, { color: '#e85d3a', weight: 3, opacity: 0.95, dashArray: '1 8', lineCap: 'round' }).addTo(map);

    var markers = [], cards = [], active = -1;
    var list = $('#stopList');

    stops.forEach(function (s, i) {
      var color = COLORS[s.category] || COLORS.default;
      var icon = L.divIcon({
        className: '',
        html: '<div class="marker-pin" style="width:40px;height:40px;background:' + color +
              ';border:3px solid #fff;box-shadow:0 3px 12px rgba(0,0,0,.4)">' + (s.emoji || s.n) + '</div>',
        iconSize: [40, 40], iconAnchor: [20, 20]
      });
      var m = L.marker([s.lat, s.lng], { icon: icon }).addTo(map)
        .bindPopup('<strong>' + s.n + '. ' + s.name + '</strong><br>' + (s.days || '') +
                   '<br>' + (s.highlights || []).slice(0, 3).map(function (h) { return '· ' + h; }).join('<br>'));
      m.on('click', function () { select(i); });
      markers.push(m);

      if (list) {
        var card = el('div', 'stop-card');
        card.innerHTML =
          '<div class="n">Parada ' + s.n + '</div>' +
          '<h4>' + (s.emoji || '') + ' ' + s.name + '</h4>' +
          '<div class="days">' + (s.days || '') + '</div>' +
          '<ul>' + (s.highlights || []).slice(0, 4).map(function (h) { return '<li>' + h + '</li>'; }).join('') + '</ul>' +
          (s.distNext ? '<div class="stop-dist">↓ ' + s.distNext + '</div>' : '');
        card.addEventListener('click', function () { select(i); });
        list.appendChild(card);
        cards.push(card);
      }
    });

    function select(i) {
      active = i;
      cards.forEach(function (c, j) { c.classList.toggle('active', i === j); });
      map.setView([stops[i].lat, stops[i].lng], 10, { animate: true });
      markers[i].openPopup();
      if (cards[i]) cards[i].scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    map.fitBounds(L.latLngBounds(coords), { padding: [60, 60] });
    window.__mapSelect = select;
  }

  // ═══════════ modal de sincronização ═══════════
  function initSync() {
    var overlay = $('#syncModal');
    if (!overlay || !window.GistSync) return;

    window.GistSync.onStatusChange(function (status) {
      var dot = $('#syncDot'), label = $('#syncLabel');
      if (!dot) return;
      dot.className = 'sync-dot ' + status;
      var texts = { idle: 'Sync desativado', syncing: 'Sincronizando…', synced: 'Sincronizado', error: 'Erro no sync' };
      if (label) label.textContent = texts[status] || '';
    });

    window.openSyncModal = function () {
      $('#syncGistId').value = localStorage.getItem(P + '_gist_id') || '';
      $('#syncPat').value = '';
      $('#syncFeedback').textContent = '';
      $('#syncDisconnect').style.display = window.GistSync.isConfigured() ? '' : 'none';
      overlay.classList.add('open');
    };
    window.closeSyncModal = function (e) {
      if (e && e.target !== e.currentTarget) return;
      overlay.classList.remove('open');
    };
    window.saveSyncConfig = function () {
      var id = $('#syncGistId').value.trim(), pat = $('#syncPat').value.trim();
      var fb = $('#syncFeedback');
      if (!id || !pat) { fb.textContent = 'Preencha Gist ID e token.'; return; }
      window.GistSync.saveCredentials(id, pat);
      fb.textContent = 'Testando…';
      window.GistSync.testConnection().then(function (ok) {
        if (!ok) { fb.textContent = 'Não consegui acessar o Gist. Confira o ID e o token.'; return; }
        window.GistSync.syncOnLoad().then(function () {
          overlay.classList.remove('open');
          location.reload();
        });
      });
    };
    window.disconnectSync = function () {
      window.GistSync.clearCredentials();
      overlay.classList.remove('open');
    };

    if (window.GistSync.isConfigured()) {
      window.GistSync.syncOnLoad().then(function (changed) { if (changed) location.reload(); });
    }
  }

  // ═══════════ boot ═══════════
  function boot() {
    initFadeIn();
    initNavSpy();
    initCalendar();
    initTodos();
    initCostSummary();
    initConverter();
    initLodging();
    initMap();
    initSync();
    window.addEventListener('fx-ready', function () { reconvert(document); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
