from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.files.storage import FileSystemStorage
import os
import pandas as pd
from .models import Movimiento
from datetime import datetime


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
    

    
def subir_cartola(request):
    if request.method == "POST" and request.FILES.get("archivo_excel"):
        archivo = request.FILES["archivo_excel"]

        # Validar extensión
        if not archivo.name.endswith(".xlsx") and not archivo.name.endswith(".xls"):
            messages.error(request, "Solo se permiten archivos Excel (.xlsx o .xls).")
            return redirect("subir_cartola")

        # Guardar archivo temporalmente
        fs = FileSystemStorage(location=os.path.join("media", "cartolas"))
        filename = fs.save(archivo.name, archivo)
        ruta_archivo = fs.path(filename)

        try:
            # Leer el Excel
            df = pd.read_excel(ruta_archivo)

            # Columnas requeridas
            columnas_requeridas = ['Fecha', 'Descripcion', 'Cargos', 'Abonos', 'Saldo']
            if not all(col in df.columns for col in columnas_requeridas):
                messages.error(request, "El archivo debe contener las columnas: Fecha, Descripcion, Cargos, Abonos, Saldo.")
                return redirect("subir_cartola")

            # Procesar y guardar
            for _, fila in df.iterrows():
                try:
                    fecha = pd.to_datetime(fila['Fecha']).date()
                except Exception:
                    continue  # si no puede convertir la fecha, pasa a la siguiente fila

                descripcion = str(fila['Descripcion'])
                cargo = float(fila['Cargos']) if not pd.isna(fila['Cargos']) else 0
                abono = float(fila['Abonos']) if not pd.isna(fila['Abonos']) else 0
                saldo = float(fila['Saldo']) if not pd.isna(fila['Saldo']) else None

                Movimiento.objects.create(
                    usuario=request.user,
                    fecha=fecha,
                    descripcion=descripcion,
                    cargo=cargo,
                    abono=abono,
                    saldo=saldo,
                    archivo_origen=archivo.name
                )

            messages.success(request, f"Archivo '{archivo.name}' cargado correctamente y {len(df)} movimientos procesados.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")

        return redirect("subir_cartola")

    return render(request, "subir_cartola.html")