/* Toggle sidebar */
function toggleSidebar() {
  const sb = document.getElementById('sidebar');
  sb.classList.toggle('collapsed');
  sb.classList.toggle('open');
}

/* Live clock */
function updateClock() {
  const el = document.getElementById('current-time');
  if (el) {
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-IN', {
      hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
    });
  }
}
setInterval(updateClock, 1000);
updateClock();

/* Check Now AJAX */
function checkNow(websiteId, btn) {
  const orig = btn.innerHTML;
  btn.innerHTML = '<span class="spinner-sm"></span> Checking…';
  btn.disabled = true;

  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
    || getCookie('csrftoken');

  fetch(`/websites/${websiteId}/check/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json',
    },
  })
  .then(r => r.json())
  .then(data => {
    // Update card UI
    const pill = document.getElementById(`status-pill-${websiteId}`);
    if (pill) {
      pill.className = `status-pill status-${data.status}`;
      pill.innerHTML = `<span class="status-dot"></span>${data.status.toUpperCase()}`;
    }
    const uptime = document.getElementById(`uptime-${websiteId}`);
    if (uptime) uptime.textContent = `${data.uptime}%`;
    const resp = document.getElementById(`response-${websiteId}`);
    if (resp) resp.textContent = data.response_time ? `${Math.round(data.response_time)}ms` : '—';

    const card = document.getElementById(`monitor-${websiteId}`);
    if (card) {
      card.className = card.className.replace(/status-(up|down|unknown)/g, `status-${data.status}`);
    }

    btn.innerHTML = '<i class="bi bi-check-lg"></i> Done';
    btn.style.color = data.status === 'up' ? '#22c55e' : '#ef4444';
    setTimeout(() => { btn.innerHTML = orig; btn.disabled = false; btn.style.color = ''; }, 2000);
  })
  .catch(() => {
    btn.innerHTML = '<i class="bi bi-x-lg"></i> Error';
    btn.style.color = '#ef4444';
    setTimeout(() => { btn.innerHTML = orig; btn.disabled = false; btn.style.color = ''; }, 2000);
  });
}

/* CSRF cookie helper */
function getCookie(name) {
  let v = null;
  document.cookie.split(';').forEach(c => {
    c = c.trim();
    if (c.startsWith(name + '=')) v = decodeURIComponent(c.substring(name.length + 1));
  });
  return v;
}

/* Auto-dismiss toasts */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert-toast').forEach((toast, i) => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      setTimeout(() => toast.remove(), 300);
    }, 4000 + i * 500);
  });
});
