// Variables globales para el carousel
let currentSlide = 0;
let autoplayInterval;

// Requisitos de contraseña
const requirements = {
    length: { regex: /.{8,}/, element: 'req-length' },
    uppercase: { regex: /[A-Z]/, element: 'req-uppercase' },
    lowercase: { regex: /[a-z]/, element: 'req-lowercase' },
    number: { regex: /[0-9]/, element: 'req-number' },
    special: { regex: /[!@#$%^&*(),.?":{}|<>]/, element: 'req-special' }
};

// Función para validar requisitos de contraseña
function validatePassword(password) {
    let isValid = true;
    
    for (let key in requirements) {
        const req = requirements[key];
        const element = document.getElementById(req.element);
        
        if (req.regex.test(password)) {
            element.classList.add('valid');
        } else {
            element.classList.remove('valid');
            isValid = false;
        }
    }
    
    return isValid;
}

// Event listener para validar en tiempo real
document.getElementById('newPassword').addEventListener('input', function() {
    const password = this.value;
    validatePassword(password);
    
    // Validar que coincidan las contraseñas
    const confirmPassword = document.getElementById('confirmPassword').value;
    if (confirmPassword) {
        checkPasswordMatch();
    }
});

// Función para verificar que las contraseñas coincidan
function checkPasswordMatch() {
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const confirmInput = document.getElementById('confirmPassword');
    
    if (confirmPassword === '') {
        confirmInput.classList.remove('valid', 'invalid');
        return false;
    }
    
    if (newPassword === confirmPassword) {
        confirmInput.classList.remove('invalid');
        confirmInput.classList.add('valid');
        return true;
    } else {
        confirmInput.classList.remove('valid');
        confirmInput.classList.add('invalid');
        return false;
    }
}

document.getElementById('confirmPassword').addEventListener('input', checkPasswordMatch);

// Función para mostrar mensajes de error
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = message;
    errorDiv.classList.add('show');
    
    setTimeout(() => {
        errorDiv.classList.remove('show');
    }, 5000);
}

// Función para mostrar/ocultar contraseña
function togglePasswordField(fieldId) {
    const passwordInput = document.getElementById(fieldId);
    passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
}

// Event listener para el formulario
document.getElementById('changePasswordForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // Validar que la nueva contraseña cumpla con los requisitos
    if (!validatePassword(newPassword)) {
        showError('La nueva contraseña no cumple con todos los requisitos.');
        return;
    }
    
    // Validar que las contraseñas coincidan
    if (newPassword !== confirmPassword) {
        showError('Las contraseñas no coinciden.');
        return;
    }
    
    // Validar que la nueva contraseña sea diferente a la actual
    if (currentPassword === newPassword) {
        showError('La nueva contraseña debe ser diferente a la actual.');
        return;
    }
    
    // Aquí iría la lógica para enviar al servidor
    console.log('Cambio de contraseña exitoso');
    console.log('Contraseña actual:', currentPassword);
    console.log('Nueva contraseña:', newPassword);
    
    alert('Contraseña cambiada exitosamente (demo)');
    
    // Limpiar formulario
    this.reset();
    
    // Resetear validaciones
    document.querySelectorAll('.password-requirements li').forEach(li => {
        li.classList.remove('valid');
    });
    document.querySelectorAll('input').forEach(input => {
        input.classList.remove('valid', 'invalid');
    });
});

// Funciones del carousel
function showSlide(n) {
    const slides = document.querySelectorAll('.carousel-slide');
    const indicators = document.querySelectorAll('.indicator');
    
    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(indicator => indicator.classList.remove('active'));
    
    if (n >= slides.length) currentSlide = 0;
    if (n < 0) currentSlide = slides.length - 1;
    
    slides[currentSlide].classList.add('active');
    indicators[currentSlide].classList.add('active');
}

function nextSlide() {
    currentSlide++;
    showSlide(currentSlide);
}

function goToSlide(n) {
    currentSlide = n;
    showSlide(currentSlide);
}

function startAutoplay() {
    autoplayInterval = setInterval(() => {
        nextSlide();
    }, 5000);
}

// Iniciar el autoplay cuando carga la página
startAutoplay();