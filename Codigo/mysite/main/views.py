from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage, default_storage
import os
import pandas as pd
from .models import Movimiento, DEFAULT_PROFILE_IMAGE
from datetime import datetime, date, timedelta
from django.db.models import Sum
import json
from django.contrib.auth.decorators import login_required
from .forms import PerfilForm, UserForm, ProfileImageForm
from .models import Perfil

# --- PÁGINAS BASE ---
def index(request):
    return render(request, 'index.html')

def cambio_clave(request):
    return render(request, 'cambio_clave.html')

def pagina_principal(request):
    if not request.user.is_authenticated:
        return redirect('login')

    hoy = date.today()
    # Rango seleccionado por el usuario (GET), por defecto mes actual
    inicio_str = request.GET.get('inicio')
    fin_str = request.GET.get('fin')
    try:
        inicio = datetime.strptime(inicio_str, '%Y-%m-%d').date() if inicio_str else hoy.replace(day=1)
    except Exception:
        inicio = hoy.replace(day=1)
    try:
        fin = datetime.strptime(fin_str, '%Y-%m-%d').date() if fin_str else hoy
    except Exception:
        fin = hoy
    if fin < inicio:
        inicio, fin = fin, inicio

    movimientos_usuario = Movimiento.objects.filter(usuario=request.user)

    # Totales del mes
    movimientos_rango = movimientos_usuario.filter(fecha__gte=inicio, fecha__lte=fin)
    total_abonos_mes = movimientos_rango.aggregate(total=Sum('abono'))['total'] or 0
    total_cargos_mes = movimientos_rango.aggregate(total=Sum('cargo'))['total'] or 0

    # Saldo actual (último registro por fecha e id)
    ultimo_mov = movimientos_usuario.order_by('-fecha', '-id').first()
    saldo_actual = ultimo_mov.saldo if ultimo_mov and ultimo_mov.saldo is not None else 0

    # Últimos movimientos
    ultimos_movimientos = movimientos_usuario.order_by('-fecha', '-id')[:10]

    # Agregados diarios del mes (ingresos/abonos y gastos/cargos)
    agregados = (
        movimientos_rango
        .values('fecha')
        .order_by('fecha')
        .annotate(abonos=Sum('abono'), cargos=Sum('cargo'))
    )

    # Generar eje de fechas desde inicio de mes a hoy
    fechas = []
    cur = inicio
    while cur <= fin:
        fechas.append(cur)
        cur += timedelta(days=1)

    mapa_abonos = {a['fecha']: (a['abonos'] or 0) for a in agregados}
    mapa_cargos = {a['fecha']: (a['cargos'] or 0) for a in agregados}

    labels = [f.strftime('%Y-%m-%d') for f in fechas]
    serie_abonos = [float(mapa_abonos.get(f, 0)) for f in fechas]
    serie_cargos = [float(mapa_cargos.get(f, 0)) for f in fechas]

    # Saldo acumulado diario: parte del último saldo antes del inicio de mes
    previo = movimientos_usuario.filter(fecha__lt=inicio).order_by('-fecha', '-id').first()
    saldo_inicio = float(previo.saldo) if previo and previo.saldo is not None else 0.0
    acumulado = saldo_inicio
    serie_saldo = []
    for f in fechas:
        acumulado += float(mapa_abonos.get(f, 0) or 0) - float(mapa_cargos.get(f, 0) or 0)
        serie_saldo.append(acumulado)

    contexto = {
        'usuario': request.user,
        'saldo_actual': saldo_actual,
        'total_abonos_mes': total_abonos_mes,
        'total_cargos_mes': total_cargos_mes,
        'ultimos_movimientos': ultimos_movimientos,
        'hoy': fin,
        'inicio': inicio,
        'fin': fin,
        # Datos para gráficos en JSON
        'chart_labels_json': json.dumps(labels),
        'chart_abonos_json': json.dumps(serie_abonos),
        'chart_cargos_json': json.dumps(serie_cargos),
        'chart_saldo_json': json.dumps(serie_saldo),
    }
    return render(request, 'pagina_principal.html', contexto)


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
        messages.info(request, f" Hasta pronto, {username}. Tu sesión se cerró correctamente.")
        return response
    else:
        # Si el usuario no estaba logueado, también lo mandamos al index
        messages.warning(request, " No tienes una sesión activa.")
        return redirect('index')
    

    
def subir_cartola(request):
    if request.method == "POST" and request.FILES.get("archivo_excel"):
        archivo = request.FILES["archivo_excel"]

        # Validar extensión
        if not archivo.name.endswith((".xlsx", ".xls")):
            messages.error(request, "Solo se permiten archivos Excel (.xlsx o .xls).")
            return redirect("subir_cartola")

        # Guardar archivo temporalmente
        carpeta_destino = os.path.join("media", "cartolas")
        os.makedirs(carpeta_destino, exist_ok=True)
        fs = FileSystemStorage(location=carpeta_destino)
        filename = fs.save(archivo.name, archivo)
        ruta_archivo = fs.path(filename)

        try:
            # Detectar motor según extensión
            if archivo.name.endswith(".xlsx"):
                df = pd.read_excel(ruta_archivo, engine="openpyxl")
            elif archivo.name.endswith(".xls"):
                df = pd.read_excel(ruta_archivo, engine="xlrd")
            else:
                raise ValueError("Formato no soportado. Usa .xls o .xlsx")

            # Validar columnas requeridas
            columnas_requeridas = ['Fecha', 'Descripcion', 'Cargos', 'Abonos', 'Saldo']
            columnas_archivo = [col.strip().capitalize() for col in df.columns]

            if not all(col in columnas_archivo for col in columnas_requeridas):
                messages.error(
                    request,
                    f"El archivo debe contener las columnas: {', '.join(columnas_requeridas)}."
                )
                return redirect("subir_cartola")

            #  Procesar filas
            registros_creados = 0
            for _, fila in df.iterrows():
                try:
                    fecha = pd.to_datetime(fila['Fecha']).date()
                    descripcion = str(fila['Descripcion'])
                    cargo = float(fila['Cargos']) if not pd.isna(fila['Cargos']) else 0
                    abono = float(fila['Abonos']) if not pd.isna(fila['Abonos']) else 0
                    saldo = float(fila['Saldo']) if not pd.isna(fila['Saldo']) else 0

                    Movimiento.objects.create(
                        usuario=request.user,
                        fecha=fecha,
                        descripcion=descripcion,
                        cargo=cargo,
                        abono=abono,
                        saldo=saldo,
                        archivo_origen=archivo.name
                    )
                    registros_creados += 1
                except Exception as fila_error:
                    print(f" Error en fila: {fila_error}")
                    continue

            messages.success(request, f"Archivo '{archivo.name}' cargado correctamente. {registros_creados} movimientos registrados.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
            print("Error procesando Excel:", e)

        return redirect("subir_cartola")

    return render(request, "subir_cartola.html")

@login_required
def configuracion(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == 'POST' and request.POST.get('form_type') == 'profile-data':
        user_form = UserForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, instance=perfil)

        if user_form.is_valid() and perfil_form.is_valid():
            user_form.save()
            perfil_form.save()
            messages.success(request, 'Tu perfil se actualizó correctamente.')
            return redirect('configuracion')
        else:
            messages.error(request, 'Revisa los campos resaltados e intenta nuevamente.')
    else:
        user_form = UserForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil)

    image_form = ProfileImageForm(instance=perfil)

    return render(request, 'configuracion.html', {
        'user_form': user_form,
        'perfil_form': perfil_form,
        'image_form': image_form,
    })


@login_required
def editar_perfil_view(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method != 'POST':
        return redirect('configuracion')

    form = ProfileImageForm(request.POST, request.FILES, instance=perfil)
    if 'profile_image' not in request.FILES:
        messages.error(request, 'Selecciona una imagen JPG o PNG válida.')
        return redirect('configuracion')

    if form.is_valid():
        old_image_name = perfil.profile_image.name if perfil.profile_image else None

        try:
            form.save()
            if (
                old_image_name
                and old_image_name != DEFAULT_PROFILE_IMAGE
                and old_image_name != perfil.profile_image.name
                and default_storage.exists(old_image_name)
            ):
                default_storage.delete(old_image_name)
            messages.success(request, 'Actualizaste tu foto de perfil.')
        except Exception as exc:
            messages.error(request, f'No pudimos guardar la imagen: {exc}')
    else:
        error_list = form.errors.get('profile_image')
        if error_list:
            messages.error(request, ' '.join(error_list))
        else:
            messages.error(request, 'La imagen no es válida.')

    return redirect('configuracion')



