// ===========================
// 🎠 CONTROL DE CARRUSEL LOGIN
// ===========================

let currentSlide = 0;
let autoplayInterval;
let isPlaying = true;

// Mostrar un slide específico
function showSlide(n) {
    const slides = document.querySelectorAll('.carousel-slide');
    const indicators = document.querySelectorAll('.indicator');

    if (slides.length === 0) return;

    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(indicator => indicator.classList.remove('active'));

    if (n >= slides.length) currentSlide = 0;
    if (n < 0) currentSlide = slides.length - 1;

    slides[currentSlide].classList.add('active');
    indicators[currentSlide].classList.add('active');
}

// Ir al siguiente slide
function nextSlide() {
    currentSlide++;
    showSlide(currentSlide);
}

// Ir al slide anterior
function prevSlide() {
    currentSlide--;
    showSlide(currentSlide);
}

// Ir a un slide específico (por los indicadores)
function goToSlide(n) {
    currentSlide = n;
    showSlide(currentSlide);
}

// Activar o pausar el autoplay
function toggleAutoplay() {
    const pauseBtn = document.querySelector('.pause-btn');
    if (isPlaying) {
        clearInterval(autoplayInterval);
        pauseBtn.textContent = '▶';
        isPlaying = false;
    } else {
        startAutoplay();
        pauseBtn.textContent = '❚❚';
        isPlaying = true;
    }
}

// Iniciar autoplay
function startAutoplay() {
    autoplayInterval = setInterval(() => {
        nextSlide();
    }, 5000);
}

// ===========================
// 👁️ MOSTRAR / OCULTAR CONTRASEÑA
// ===========================
function togglePassword() {
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
    }
}

// ===========================
// 🚀 FORMULARIO DE LOGIN (Django real)
// ===========================
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            const username = document.getElementById('username')?.value || "(sin usuario)";
            const password = document.getElementById('password')?.value ? "********" : "(vacía)";

            console.log("📨 Enviando formulario de login a Django...");
            console.log("Usuario:", username);
            console.log("Contraseña:", password);
            // ⚠️ No usamos preventDefault para permitir POST real al backend
        });
    }

    // Inicia el autoplay del carrusel
    startAutoplay();
});
