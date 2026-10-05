document.documentElement.classList.add('js');
const english=document.documentElement.lang==='en';
const header=document.querySelector('.site-header');
const toggle=document.querySelector('.menu-toggle');
const nav=document.querySelector('.nav-links');
const mobile=window.matchMedia('(max-width:1000px)');
const solidHeader=document.querySelector('main')?.classList.contains('legal');
const onScroll=()=>header?.classList.toggle('scrolled',solidHeader||window.scrollY>30);
window.addEventListener('scroll',onScroll,{passive:true});onScroll();
function setMenu(open,restoreFocus=false){if(!nav||!toggle)return;nav.classList.toggle('open',open);nav.inert=mobile.matches&&!open;toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?(english?'Close menu':'Menü schließen'):(english?'Open menu':'Menü öffnen'));toggle.textContent=open?'×':'☰';if(restoreFocus)toggle.focus();}
toggle?.addEventListener('click',()=>setMenu(!nav.classList.contains('open')));
nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>setMenu(false)));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&nav?.classList.contains('open'))setMenu(false,true)});
document.addEventListener('click',e=>{if(mobile.matches&&nav?.classList.contains('open')&&!nav.contains(e.target)&&!toggle.contains(e.target))setMenu(false)});
mobile.addEventListener('change',()=>setMenu(false));setMenu(false);
if('IntersectionObserver' in window){const io=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target)}}),{threshold:.05});document.querySelectorAll('.reveal').forEach(el=>io.observe(el));}else document.querySelectorAll('.reveal').forEach(el=>el.classList.add('visible'));
document.querySelectorAll('[data-year]').forEach(el=>el.textContent=new Date().getFullYear());
