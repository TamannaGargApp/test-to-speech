/* ═══════════════════════════════════════════════════════════════
   VoiceForge — Auth helpers
═══════════════════════════════════════════════════════════════ */

const API_BASE = '';

// Google OAuth client ID (public). Must match GOOGLE_CLIENT_ID in the backend .env.
const GOOGLE_CLIENT_ID = '210393640285-40g457h3e83gaanjsjr1eh7hlqumk4l7.apps.googleusercontent.com';

function _showToast(msg, type = '') {
  const t = document.getElementById('toast');
  if (!t) { alert(msg); return; }
  t.innerHTML = (type === 'error' ? '⚠ ' : type === 'success' ? '✓ ' : '') + msg;
  t.className = 'show' + (type ? ' ' + type : '');
  setTimeout(() => { t.className = ''; }, 3200);
}

async function login() {
  const email    = document.getElementById('email')?.value?.trim();
  const password = document.getElementById('password')?.value;

  if (!email || !password) {
    _showToast('Please fill in all fields.', 'error');
    return;
  }

  try {
    const res = await fetch(`/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      _showToast(err.detail || 'Invalid email or password.', 'error');
      return;
    }

    const data = await res.json();
    localStorage.setItem('token', data.access_token || data.token);
    localStorage.setItem('userEmail', email);
    _showToast('Signed in!', 'success');
    setTimeout(() => { window.location.href = 'dashboard.html'; }, 600);
  } catch {
    _showToast('Network error. Is the server running?', 'error');
  }
}

async function register() {
  const email    = document.getElementById('email')?.value?.trim();
  const password = document.getElementById('password')?.value;

  if (!email || !password) {
    _showToast('Please fill in all fields.', 'error');
    return;
  }

  if (password.length < 8) {
    _showToast('Password must be at least 8 characters.', 'error');
    return;
  }

  try {
    const res = await fetch(`/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      _showToast(err.detail || 'Registration failed. Try again.', 'error');
      return;
    }

    _showToast('Account created! Signing you in…', 'success');
    setTimeout(async () => { await login(); }, 800);
  } catch {
    _showToast('Network error. Is the server running?', 'error');
  }
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('userEmail');
  window.location.href = 'login.html';
}

/* ── Google sign-in ──────────────────────────────────────────── */

function googleSignIn() {
  // Redirect flow (avoids COOP/popup issues). Google returns to login.html.
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  const nonce = Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
  sessionStorage.setItem('googleNonce', nonce);

  const redirectUri = encodeURIComponent(window.location.origin + '/login.html');
  const scope = encodeURIComponent('openid email profile');
  window.location.href = 'https://accounts.google.com/o/oauth2/v2/auth'
    + '?client_id=' + GOOGLE_CLIENT_ID
    + '&redirect_uri=' + redirectUri
    + '&response_type=token%20id_token'
    + '&scope=' + scope
    + '&nonce=' + nonce;
}

// Called on login.html: sends Google's ID token to the backend, which verifies it.
async function handleGoogleRedirect() {
  const hash = window.location.hash;
  if (!hash.includes('id_token')) return;

  const params = new URLSearchParams(hash.substring(1));
  const idToken = params.get('id_token');
  const nonce = sessionStorage.getItem('googleNonce');
  history.replaceState(null, '', window.location.pathname);
  sessionStorage.removeItem('googleNonce');
  if (!idToken) return;
  if (!nonce) {
    _showToast('Google sign-in expired. Please click "Continue with Google" again.', 'error');
    return;
  }

  _showToast('Signing you in...');

  try {
    const res = await fetch('/api/auth/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken, nonce })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      _showToast(err.detail || 'Google sign-in failed. Try email instead.', 'error');
      return;
    }

    const data = await res.json();
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('userEmail', data.email);
    _showToast('Signed in with Google!', 'success');
    setTimeout(() => { window.location.href = 'dashboard.html'; }, 700);
  } catch {
    _showToast('Google sign-in failed.', 'error');
  }
}
