from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout


# --- PÁGINAS BASE ---
def index(request):
    return render(request, 'index.html')

def cambio_clave(request):
    return render(request, 'cambio_clave.html')

def pagina_principal(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'pagina_principal.html', {'usuario': request.user})


# --- LOGIN REAL ---
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Intentar autenticar usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}")
            return redirect('pagina_principal')
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login')

    return render(request, 'login.html')


# --- REGISTRO DE USUARIOS ---
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está en uso.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Ya existe una cuenta con este correo.")
            return redirect("register")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        messages.success(request, "Cuenta creada exitosamente. ¡Ahora puedes iniciar sesión!")
        return redirect("login")

    return render(request, "register.html")


# --- CERRAR SESIÓN ---
# --- LOGOUT (mejorado) ---


def logout_view(request):
    """
    Cierra la sesión del usuario de forma segura, limpia la caché y redirige al index.
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)

        # Evita que el usuario use el botón “Atrás” para volver a una página protegida
        response = redirect('index')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        # Mensaje de despedida
        messages.info(request, f"👋 Hasta pronto, {username}. Tu sesión se cerró correctamente.")
        return response
    else:
        # Si el usuario no estaba logueado, también lo mandamos al index
        messages.warning(request, "⚠️ No tienes una sesión activa.")
        return redirect('index')