/* ═══════════════════════════════════════════════════════════════
   VoiceForge — shared UI behaviour for the app pages
   • mobile menu button + slide-in sidebar
   • working sidebar links and the active page highlight
   • time-of-day greeting on the dashboard
═══════════════════════════════════════════════════════════════ */
(function () {
  const page = (location.pathname.split('/').pop() || 'index.html').toLowerCase();

  /* Sidebar links: some pages had placeholder "#" links */
  const LINKS = {
    'dashboard': 'dashboard.html',
    'studio': 'studio.html',
    'speech to text': 'transcribe.html',
    'history': 'history.html',
    'voices': 'voices.html',
    'api': 'api.html',
  };
  document.querySelectorAll('.sb-nav .nav-item').forEach(a => {
    const label = a.textContent.replace(/new/i, '').trim().toLowerCase();
    if (LINKS[label] && a.getAttribute('href') === '#') a.setAttribute('href', LINKS[label]);
    a.classList.toggle('active', (a.getAttribute('href') || '').toLowerCase() === page);
  });

  /* Mobile drawer */
  const sidebar = document.querySelector('.shell .sb');
  const topbar = document.querySelector('.topbar');
  if (sidebar && topbar) {
    const overlay = document.createElement('div');
    overlay.className = 'vf-overlay';
    document.body.appendChild(overlay);

    const btn = document.createElement('button');
    btn.className = 'vf-menu-btn';
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Open menu');
    btn.setAttribute('aria-expanded', 'false');
    btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M3 5h12M3 9h12M3 13h12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
    topbar.prepend(btn);

    const setOpen = open => {
      document.body.classList.toggle('vf-nav-open', open);
      btn.setAttribute('aria-expanded', String(open));
    };
    btn.addEventListener('click', () => setOpen(!document.body.classList.contains('vf-nav-open')));
    overlay.addEventListener('click', () => setOpen(false));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') setOpen(false); });
    sidebar.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setOpen(false)));
  }

  /* Dashboard greeting that matches the time of day */
  const title = document.querySelector('.page-title');
  if (title && /^Good (morning|afternoon|evening)/.test(title.textContent)) {
    const h = new Date().getHours();
    const part = h < 12 ? 'morning' : h < 18 ? 'afternoon' : 'evening';
    title.textContent = title.textContent.replace(/morning|afternoon|evening/, part);
  }
})();

/* ── History playback (Dashboard + History) ─────────────────── */
const VF_VOICE_NAMES = {
  aria: 'Aria', atlas: 'Atlas', nova: 'Nova', echo: 'Echo', luna: 'Luna', rex: 'Rex',
  sage: 'Sage', orion: 'Orion', claire: 'Claire', james: 'James',
  hi_swara: 'Swara', hi_madhur: 'Madhur', es_elvira: 'Elvira', es_alvaro: 'Álvaro',
  fr_denise: 'Denise', fr_henri: 'Henri', de_katja: 'Katja', de_konrad: 'Konrad',
  ja_nanami: 'Nanami', ja_keita: 'Keita',
};
function vfVoiceName(id) { return VF_VOICE_NAMES[(id || 'aria').toLowerCase()] || id; }

let vfAudio = null, vfAudioBtn = null;
const vfAudioCache = {};

function vfResetPlayBtn() {
  if (vfAudioBtn) { vfAudioBtn.textContent = '▶'; vfAudioBtn.classList.remove('playing'); }
  vfAudioBtn = null;
}

async function vfPlayHistory(btn, id) {
  // Clicking the playing row again pauses it
  if (vfAudio && vfAudioBtn === btn && !vfAudio.paused) { vfAudio.pause(); vfResetPlayBtn(); return; }
  if (vfAudio) vfAudio.pause();
  vfResetPlayBtn();

  vfAudioBtn = btn;
  btn.textContent = '…';
  try {
    if (!vfAudioCache[id]) {
      const res = await fetch('/api/history/' + encodeURIComponent(id) + '/audio', {
        headers: { 'Authorization': 'Bearer ' + localStorage.getItem('token') }
      });
      if (!res.ok) {
        const e = await res.json().catch(() => ({}));
        throw new Error(e.detail || 'Could not load this audio.');
      }
      vfAudioCache[id] = URL.createObjectURL(await res.blob());
    }
    if (vfAudioBtn !== btn) return;  // another row was clicked meanwhile
    vfAudio = new Audio(vfAudioCache[id]);
    vfAudio.onended = vfResetPlayBtn;
    await vfAudio.play();
    btn.textContent = '❚❚';
    btn.classList.add('playing');
  } catch (e) {
    vfResetPlayBtn();
    if (typeof showToast === 'function') showToast(e.message || 'Could not play this audio.', 'error');
  }
}


/* ── Profile menu in the sidebar (click your name/email → Log out) ── */
function vfLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('userEmail');
  window.location.href = 'login.html';
}
(function () {
  const row = document.querySelector('.sb .user-row');
  if (!row) return;
  const foot = row.parentElement;
  foot.classList.add('vf-profile');

  // The old icon is replaced by a chevron; logging out now lives in the menu
  const oldBtn = row.querySelector('.logout-btn');
  if (oldBtn) oldBtn.remove();
  const chev = document.createElement('span');
  chev.className = 'vf-chev';
  chev.innerHTML = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M4 8.5L7 5.5l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  row.appendChild(chev);

  row.setAttribute('role', 'button');
  row.setAttribute('tabindex', '0');
  row.setAttribute('aria-haspopup', 'menu');
  row.setAttribute('aria-expanded', 'false');
  row.title = 'Account';

  const email = localStorage.getItem('userEmail') || 'user@example.com';
  const icon = p => '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">' + p + '</svg>';
  const menu = document.createElement('div');
  menu.className = 'vf-menu';
  menu.setAttribute('role', 'menu');
  menu.innerHTML =
    '<div class="vf-menu-head"><div class="vf-menu-av"></div><div style="min-width:0"><div class="vf-menu-email"></div><div class="vf-menu-plan">Free plan</div></div></div>' +
    '<a role="menuitem" href="dashboard.html">' + icon('<rect x="2" y="2" width="5" height="5" rx="1"/><rect x="9" y="2" width="5" height="5" rx="1"/><rect x="2" y="9" width="5" height="5" rx="1"/><rect x="9" y="9" width="5" height="5" rx="1"/>') + 'Dashboard</a>' +
    '<a role="menuitem" href="history.html">' + icon('<circle cx="8" cy="8" r="6"/><path d="M8 5v3l2 1.5"/>') + 'History</a>' +
    '<div class="vf-menu-sep"></div>' +
    '<button role="menuitem" type="button" class="vf-menu-logout">' + icon('<path d="M6 2.5H3.5a1 1 0 00-1 1v9a1 1 0 001 1H6M10.5 11l3-3-3-3M13.5 8H6"/>') + 'Log out</button>';
  menu.querySelector('.vf-menu-av').textContent = email[0].toUpperCase();
  menu.querySelector('.vf-menu-email').textContent = email;
  menu.querySelector('.vf-menu-logout').addEventListener('click', vfLogout);
  foot.appendChild(menu);

  const setOpen = open => {
    // Sit just above the profile row, covering the usage box
    if (open) menu.style.bottom = (foot.clientHeight - row.offsetTop + 6) + 'px';
    foot.classList.toggle('open', open);
    row.setAttribute('aria-expanded', String(open));
  };
  row.addEventListener('click', e => { e.stopPropagation(); setOpen(!foot.classList.contains('open')); });
  row.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setOpen(!foot.classList.contains('open')); } });
  document.addEventListener('click', e => { if (!foot.contains(e.target)) setOpen(false); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') setOpen(false); });
})();
