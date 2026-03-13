
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const mobileClose = document.getElementById('mobileClose');


function openMenu(){
  mobileMenu.classList.add('open');
  hamburger.classList.add('active');
  document.body.style.overflow='hidden';
}


function closeMenu(){
  mobileMenu.classList.remove('open');
  hamburger.classList.remove('active');
  document.body.style.overflow='';
}


hamburger.addEventListener('click', openMenu);
mobileClose.addEventListener('click', closeMenu);


// Close on outside click
mobileMenu.addEventListener('click', function(e){
  if(e.target === mobileMenu) closeMenu();
});


// Close on Escape key
document.addEventListener('keydown', function(e){
  if(e.key === 'Escape') closeMenu();
});
