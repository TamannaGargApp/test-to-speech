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
