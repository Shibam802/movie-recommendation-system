/* ── CineMatch — main.js ───────────────────────────────────────────────── */
const API      = '';
const OMDB_KEY = '5eabc757';

let allMovies = [];

// ── Poster fetcher ─────────────────────────────────────────────────────────
const posterCache = {};

async function fetchPoster(title) {
  if (posterCache[title]) return posterCache[title];
  try {
    const r = await fetch(`https://www.omdbapi.com/?t=${encodeURIComponent(title)}&apikey=${OMDB_KEY}`);
    const d = await r.json();
    const url = (d.Poster && d.Poster !== 'N/A') ? d.Poster : null;
    posterCache[title] = url;
    return url;
  } catch { return null; }
}

// ── Utility ────────────────────────────────────────────────────────────────
const $  = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function showToast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

function setLoading(on) {
  $('#loadingOverlay').style.display = on ? 'flex' : 'none';
}

const EMOJIS = ['🎬','🎭','🎥','🎞️','🍿','⭐','🌟','🔥','💫','🎦'];
function randEmoji() { return EMOJIS[Math.floor(Math.random() * EMOJIS.length)]; }

// ── Views ───────────────────────────────────────────────────────────────────
function showView(name) {
  ['home','history','popular','admin'].forEach(v => {
    const el = $(`#view-${v}`);
    if (el) el.style.display = (v === name) ? '' : 'none';
  });
  $$('.nav-btn').forEach(b => b.classList.toggle('active', b.dataset.view === name));

  if (name === 'history') loadHistory();
  if (name === 'popular') loadPopular();
  if (name === 'admin')   loadStats();
}

$$('.nav-btn').forEach(btn => {
  btn.addEventListener('click', () => showView(btn.dataset.view));
});

// ── Fetch movies list ────────────────────────────────────────────────────────
async function loadMovies() {
  try {
    const r = await fetch(`${API}/api/movies`);
    const d = await r.json();
    allMovies = d.movies || [];
  } catch (e) {
    console.warn('Could not load movies list');
  }
}

// ── Autocomplete ─────────────────────────────────────────────────────────────
const input = $('#movieInput');
const acList = $('#autocompleteList');

input.addEventListener('input', () => {
  const q = input.value.trim().toLowerCase();
  acList.innerHTML = '';
  if (!q || q.length < 2) return;

  const matches = allMovies
    .filter(m => m.toLowerCase().includes(q))
    .slice(0, 8);

  matches.forEach(movie => {
    const item = document.createElement('div');
    item.className = 'autocomplete-item';
    item.textContent = movie;
    item.addEventListener('click', () => {
      input.value = movie;
      acList.innerHTML = '';
      doSearch(movie);
    });
    acList.appendChild(item);
  });
});

document.addEventListener('click', (e) => {
  if (!e.target.closest('.search-box')) acList.innerHTML = '';
});

input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    acList.innerHTML = '';
    doSearch(input.value.trim());
  }
});

$('#searchBtn').addEventListener('click', () => doSearch(input.value.trim()));

// ── Quick Pills ───────────────────────────────────────────────────────────────
$$('.pill').forEach(pill => {
  pill.addEventListener('click', () => {
    const m = pill.dataset.movie;
    input.value = m;
    doSearch(m);
  });
});

// ── Recommend ────────────────────────────────────────────────────────────────
async function doSearch(movie) {
  if (!movie) { showToast('Please enter a movie title'); return; }

  setLoading(true);
  $('#resultsSection').style.display = 'none';

  try {
    const r = await fetch(`${API}/api/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ movie })
    });
    const d = await r.json();

    if (!r.ok) {
      showToast(d.error || 'Movie not found');
      setLoading(false);
      return;
    }

    await renderResults(d.movie, d.recommendations);
  } catch (e) {
    showToast('Server error. Is the backend running?');
    console.error(e);
  } finally {
    setLoading(false);
  }
}

async function renderResults(movie, recs) {
  $('#resultsMovieTitle').textContent = movie;
  const grid = $('#cardsGrid');
  grid.innerHTML = '';

  // Fetch all posters in parallel
  const posters = await Promise.all(recs.map(r => fetchPoster(r.title)));

  recs.forEach((rec, idx) => {
    const card = document.createElement('div');
    card.className = 'movie-card';
    const poster = posters[idx];
    const posterHTML = poster
      ? `<img class="card-poster-img" src="${poster}" alt="${rec.title}" loading="lazy"/>`
      : `<div class="card-poster">${randEmoji()}</div>`;

    card.innerHTML = `
      <div class="card-rank">${String(idx + 1).padStart(2,'0')}</div>
      ${posterHTML}
      <div class="card-title">${rec.title}</div>
      <div class="card-score">◈ ${rec.score}% match</div>
      <div class="card-actions">
        <button class="rate-btn" data-movie="${rec.title}" data-rating="5">★ Love it</button>
        <button class="rate-btn" data-movie="${rec.title}" data-rating="3">👍 Maybe</button>
      </div>
    `;
    grid.appendChild(card);
  });

  // Rating buttons
  $$('.rate-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      await rateMovie(btn.dataset.movie, parseInt(btn.dataset.rating));
      btn.classList.add('rated');
      btn.textContent = '✓ Rated';
    });
  });

  $('#resultsSection').style.display = 'block';
  $('#resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

$('#clearBtn').addEventListener('click', () => {
  $('#resultsSection').style.display = 'none';
  input.value = '';
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ── Rating ────────────────────────────────────────────────────────────────────
async function rateMovie(movie, rating) {
  try {
    await fetch(`${API}/api/rate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ movie, rating })
    });
    showToast(`Rated "${movie}" ${rating}/5 ⭐`);
  } catch (e) {
    console.warn('Rating error', e);
  }
}

// ── History ───────────────────────────────────────────────────────────────────
async function loadHistory() {
  const list = $('#historyList');
  list.innerHTML = '<p style="color:var(--text-muted)">Loading…</p>';
  try {
    const r = await fetch(`${API}/api/history`);
    const d = await r.json();
    if (!d.history.length) {
      list.innerHTML = '<p style="color:var(--text-muted)">No searches yet. Start by searching a movie!</p>';
      return;
    }
    list.innerHTML = d.history.map(h => `
      <div class="history-item">
        <div class="history-movie">${h.movie}</div>
        <div class="history-recs">
          ${h.recommendations.map(r => `<span class="history-rec-pill">${r}</span>`).join('')}
        </div>
        <div class="history-date">${new Date(h.searched_at).toLocaleDateString()}</div>
      </div>
    `).join('');
  } catch (e) {
    list.innerHTML = '<p style="color:var(--text-muted)">Could not load history</p>';
  }
}

// ── Popular ────────────────────────────────────────────────────────────────────
async function loadPopular() {
  const list = $('#popularList');
  list.innerHTML = '<p style="color:var(--text-muted)">Loading…</p>';
  try {
    const r = await fetch(`${API}/api/popular`);
    const d = await r.json();
    if (!d.popular.length) {
      list.innerHTML = '<p style="color:var(--text-muted)">No trending data yet.</p>';
      return;
    }
    list.innerHTML = d.popular.map((p, i) => `
      <div class="popular-item" style="animation-delay:${i*0.06}s">
        <div class="popular-rank">${String(i+1).padStart(2,'0')}</div>
        <div class="popular-name">${p.title}</div>
        <div class="popular-count">${p.count} search${p.count > 1 ? 'es' : ''}</div>
      </div>
    `).join('');
  } catch (e) {
    list.innerHTML = '<p style="color:var(--text-muted)">Could not load trending</p>';
  }
}

// ── Stats / Admin ──────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const r = await fetch(`${API}/api/stats`);
    const d = await r.json();
    $('#statsGrid').innerHTML = `
      <div class="stat-card"><div class="stat-number">${d.total_movies}</div><div class="stat-label">Movies in DB</div></div>
      <div class="stat-card"><div class="stat-number">${d.total_searches}</div><div class="stat-label">Total Searches</div></div>
      <div class="stat-card"><div class="stat-number">${d.unique_movies}</div><div class="stat-label">Unique Searched</div></div>
      <div class="stat-card"><div class="stat-number">${d.avg_rating || '—'}</div><div class="stat-label">Avg Rating</div></div>
    `;
  } catch (e) {
    $('#statsGrid').innerHTML = '<p style="color:var(--text-muted)">Could not load stats</p>';
  }
}

$('#trainBtn').addEventListener('click', async () => {
  const status = $('#trainStatus');
  const btn = $('#trainBtn');
  btn.disabled = true; btn.textContent = '⚙ Training…';
  status.className = 'train-status';
  status.textContent = 'Training model, please wait…';
  try {
    const r = await fetch(`${API}/api/train`, { method: 'POST' });
    const d = await r.json();
    if (r.ok) {
      status.className = 'train-status success';
      status.textContent = '✓ ' + d.message;
    } else {
      status.className = 'train-status error';
      status.textContent = '✗ ' + d.error;
    }
  } catch (e) {
    status.className = 'train-status error';
    status.textContent = '✗ Server error during training';
  } finally {
    btn.disabled = false; btn.textContent = '⚙ Train Model';
  }
});

// ── Init ───────────────────────────────────────────────────────────────────────
loadMovies();
