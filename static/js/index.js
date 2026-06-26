// ===== CBT Platform — Interactions =====

// Page Loader
window.addEventListener('load', () => {
  const loader = document.querySelector('.loader');
  if (loader) setTimeout(() => loader.classList.add('hidden'), 400);
});

// Sticky navbar
const navbar = document.querySelector('.navbar');
const onScroll = () => {
  if (!navbar) return;
  navbar.classList.toggle('scrolled', window.scrollY > 30);
};
window.addEventListener('scroll', onScroll);
onScroll();

// Mobile menu toggle
const toggleBtn = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');
if (toggleBtn && navLinks) {
  toggleBtn.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    const icon = toggleBtn.querySelector('i');
    if (icon) icon.className = navLinks.classList.contains('open') ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
  });
  navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    const icon = toggleBtn.querySelector('i');
    if (icon) icon.className = 'fa-solid fa-bars';
  }));
}

// Active nav highlighting based on file
const currentPage = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
document.querySelectorAll('.nav-links a').forEach(a => {
  const href = (a.getAttribute('href') || '').toLowerCase();
  if (href === currentPage || (currentPage === '' && href === 'index.html')) a.classList.add('active');
});

// FAQ accordion
document.querySelectorAll('.faq-item').forEach(item => {
  const q = item.querySelector('.faq-q');
  if (!q) return;
  q.addEventListener('click', () => {
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

// Scroll Reveal
const revealEls = document.querySelectorAll('.reveal');
const io = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('visible');
      io.unobserve(e.target);
    }
  });
}, { threshold: 0.12 });
revealEls.forEach(el => io.observe(el));

// Animated counters
const counters = document.querySelectorAll('[data-counter]');
const counterIO = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    const el = e.target;
    const target = +el.dataset.counter;
    const suffix = el.dataset.suffix || '';
    const duration = 1800;
    const start = performance.now();
    const step = (now) => {
      const p = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.floor(target * ease).toLocaleString() + suffix;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
    counterIO.unobserve(el);
  });
}, { threshold: 0.4 });
counters.forEach(c => counterIO.observe(c));

// Pricing toggle
const toggle = document.querySelector('.toggle');
const monthLabel = document.querySelector('[data-bill="monthly"]');
const yearLabel = document.querySelector('[data-bill="yearly"]');
if (toggle) {
  toggle.addEventListener('click', () => {
    const yearly = toggle.classList.toggle('yearly');
    document.querySelectorAll('.price').forEach(p => {
      const m = p.dataset.monthly;
      const y = p.dataset.yearly;
      if (!m || !y) return;
      p.firstChild.textContent = yearly ? y : m;
    });
    document.querySelectorAll('[data-period]').forEach(s => {
      s.textContent = yearly ? '/year' : '/month';
    });
    if (monthLabel && yearLabel) {
      monthLabel.classList.toggle('active-bill', !yearly);
      yearLabel.classList.toggle('active-bill', yearly);
    }
  });
}

// Newsletter form
const newsForm = document.querySelector('.news-form');
if (newsForm) {
  newsForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = newsForm.querySelector('input');
    const btn = newsForm.querySelector('button');
    if (input && input.value.trim()) {
      btn.innerHTML = '<i class="fa-solid fa-check"></i> Subscribed';
      input.value = '';
      setTimeout(() => { btn.innerHTML = 'Subscribe'; }, 2500);
    }
  });
}
