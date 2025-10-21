// Variables globales
let currentSlide = 0;
let autoplayInterval;
let isPlaying = true;

// Función para mostrar un slide específico
function showSlide(n) {
    const slides = document.querySelectorAll('.carousel-slide');
    const indicators = document.querySelectorAll('.indicator');
    
    // Remover clase active de todos los slides e indicadores
    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(indicator => indicator.classList.remove('active'));
    
    // Manejar el ciclo del carousel
    if (n >= slides.length) currentSlide = 0;
    if (n < 0) currentSlide = slides.length - 1;
    
    // Activar el slide e indicador actual
    slides[currentSlide].classList.add('active');
    indicators[currentSlide].classList.add('active');
}

// Función para ir al siguiente slide
function nextSlide() {
    currentSlide++;
    showSlide(currentSlide);
}

// Función para ir al slide anterior
function prevSlide() {
    currentSlide--;
    showSlide(currentSlide);
}

// Función para ir a un slide específico
function goToSlide(n) {
    currentSlide = n;
    showSlide(currentSlide);
}

// Función para activar/desactivar el autoplay
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

// Función para iniciar el autoplay
function startAutoplay() {
    autoplayInterval = setInterval(() => {
        nextSlide();
    }, 5000);
}

// Función para mostrar/ocultar contraseña
function togglePassword() {
    const passwordInput = document.getElementById('password');
    passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
}

// Event listener para el formulario de login
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const rut = document.getElementById('rut').value;
    const password = document.getElementById('password').value;
    
    // Aquí puedes agregar la lógica de validación y envío
    console.log('RUT:', rut);
    console.log('Password:', password);
    
    alert('Formulario enviado (demo)');
});

// Iniciar el autoplay cuando carga la página
startAutoplay();