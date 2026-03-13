
/* ── Page navigation ──────────────────────── */
const pageTitles = {
  dashboard: 'Dashboard',
  exams:     'Exams',
  results:   'Results',
  payment:   'Payment',
  profile:   'My Profile'
};


function showPage(id, navEl) {
  // hide all pages
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  // deactivate all nav items
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  // show target
  document.getElementById('page-' + id).classList.add('active');
  // activate nav
  if (navEl) navEl.classList.add('active');
  // update title
  document.getElementById('pageTitle').textContent = pageTitles[id] || id;
  // close sidebar on mobile
  closeSidebar();
}


/* ── Sidebar toggle ───────────────────────── */
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('overlay').classList.toggle('open');
}


function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('overlay').classList.remove('open');
}


/* ── Plan selector ────────────────────────── */
function selectPlan(el) {
  document.querySelectorAll('.plan-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
}


/* ── Card number formatter ────────────────── */
document.addEventListener('input', function(e) {
  if (e.target.placeholder === '0000 0000 0000 0000') {
    let v = e.target.value.replace(/\D/g, '').substring(0, 16);
    e.target.value = v.replace(/(.{4})/g, '$1 ').trim();
  }
  if (e.target.placeholder === 'MM / YY') {
    let v = e.target.value.replace(/\D/g, '').substring(0, 4);
    if (v.length >= 2) v = v.slice(0,2) + ' / ' + v.slice(2);
    e.target.value = v;
  }
});


/* ── Animate progress bars on profile load ── */
document.querySelectorAll('.nav-item').forEach(item => {
  if (item.textContent.trim().startsWith('My Profile')) {
    item.addEventListener('click', () => {
      setTimeout(() => {
        document.querySelectorAll('.progress-bar-fill').forEach((bar, i) => {
          bar.style.width = [65, 80, 45, 72][i % 4] + '%';
        });
      }, 100);
    });
  }
});
