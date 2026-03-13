
const hamburger=document.getElementById("hamburger");
const mobileMenu=document.getElementById("mobileMenu");

hamburger.addEventListener("click",()=>{
mobileMenu.classList.toggle("open");
document.body.style.overflow=mobileMenu.classList.contains("open")?"hidden":"";
});

function closeMobileMenu(){
mobileMenu.classList.remove("open");
document.body.style.overflow="";
}
