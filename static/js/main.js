const menuBtn = document.getElementById('menuBtn');
const navLinks = document.getElementById('navLinks');
if (menuBtn && navLinks) {
  menuBtn.addEventListener('click', () => navLinks.classList.toggle('show'));
}

const searchInput = document.getElementById('siteSearch');
const cards = document.querySelectorAll('.searchable-card');
if (searchInput && cards.length) {
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim().toLowerCase();
    cards.forEach((card) => {
      const haystack = card.dataset.search || '';
      card.style.display = haystack.includes(query) ? '' : 'none';
    });
  });
}

