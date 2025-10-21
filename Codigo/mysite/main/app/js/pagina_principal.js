// Función para manejar la navegación del sidebar
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Remover clase active de todos los items
        document.querySelectorAll('.nav-item').forEach(nav => {
            nav.classList.remove('active');
        });
        
        // Agregar clase active al item clickeado
        this.classList.add('active');
        
        // Aquí puedes agregar la lógica para cambiar de vista
        console.log('Navegando a:', this.querySelector('span').textContent);
    });
});

// Función para manejar el botón de pantalla completa
document.querySelector('.btn-fullscreen')?.addEventListener('click', function() {
    const embedContainer = document.querySelector('.dashboard-embed');
    
    if (!document.fullscreenElement) {
        embedContainer.requestFullscreen().catch(err => {
            console.log('Error al intentar pantalla completa:', err);
        });
    } else {
        document.exitFullscreen();
    }
});

// Función para manejar el cierre de sesión
document.querySelector('.logout-btn')?.addEventListener('click', function(e) {
    e.preventDefault();
    
    if (confirm('¿Estás seguro que deseas cerrar sesión?')) {
        // Aquí iría la lógica para cerrar sesión
        console.log('Cerrando sesión...');
        // window.location.href = 'index.html'; // Redirigir al login
    }
});

// Función para animar los valores numéricos al cargar
function animateValue(element, start, end, duration) {
    if (!element) return;
    
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        
        // Formatear con separador de miles
        element.textContent = '$' + Math.floor(current).toLocaleString('es-CL');
    }, 16);
}

// Animar los valores al cargar la página
window.addEventListener('load', () => {
    const balanceElement = document.querySelector('.card-balance .card-value');
    const incomeElement = document.querySelector('.card-income');
    const expensesElement = document.querySelector('.card-expenses');
    
    if (balanceElement) animateValue(balanceElement, 0, 8950, 1000);
    if (incomeElement) animateValue(incomeElement, 0, 4500, 1200);
    if (expensesElement) animateValue(expensesElement, 0, 1300, 1400);
});

// Función para búsqueda (opcional)
const searchInput = document.querySelector('.search-bar input');
searchInput?.addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    console.log('Buscando:', searchTerm);
    // Aquí puedes agregar la lógica de búsqueda
});

// Detectar cambio de pantalla completa
document.addEventListener('fullscreenchange', () => {
    const btn = document.querySelector('.btn-fullscreen');
    if (document.fullscreenElement) {
        console.log('Modo pantalla completa activado');
    } else {
        console.log('Modo pantalla completa desactivado');
    }
});