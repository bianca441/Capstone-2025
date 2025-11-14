from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.paginator import Paginator
import os
import pandas as pd
from .models import Movimiento, DEFAULT_PROFILE_IMAGE, CuentaBanco, Perfil, CategoriaGasto
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.db.models import Sum, Min, Max
from django.db.models.functions import TruncMonth
import json
from django.contrib.auth.decorators import login_required
from .forms import PerfilForm, UserForm, ProfileImageForm, CuentaBancoForm, CategoriaGastoForm

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
    def parse_param(valor, fallback):
        if not valor:
            return fallback
        for fmt in ('%d-%m-%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(valor, fmt).date()
            except ValueError:
                continue
        return fallback

    inicio = parse_param(request.GET.get('inicio'), hoy.replace(day=1))
    fin = parse_param(request.GET.get('fin'), hoy)
    if fin < inicio:
        inicio, fin = fin, inicio

    cuentas_usuario = CuentaBanco.objects.filter(usuario=request.user).order_by('nombre_identificador')
    cuenta_param = request.GET.get('cuenta', 'todas')
    movimientos_usuario = Movimiento.objects.filter(usuario=request.user)
    cuenta_seleccionada = None

    if cuenta_param != 'todas':
        try:
            cuenta_seleccionada = cuentas_usuario.get(pk=int(cuenta_param))
            movimientos_usuario = movimientos_usuario.filter(cuenta=cuenta_seleccionada)
            cuenta_param = str(cuenta_seleccionada.pk)
        except (ValueError, CuentaBanco.DoesNotExist):
            cuenta_param = 'todas'

    def saldo_desde_cuentas(cuentas, fecha_limite=None):
        total = Decimal('0')
        tiene_cuentas = False
        for cuenta in cuentas:
            tiene_cuentas = True
            saldo_base = Decimal(cuenta.saldo_inicial or 0)
            movs = cuenta.movimientos.all()
            if fecha_limite is not None:
                movs = movs.filter(fecha__lt=fecha_limite)
            agregados = movs.aggregate(
                total_cargos=Sum('cargo'),
                total_abonos=Sum('abono')
            )
            cargos = Decimal(agregados['total_cargos'] or 0)
            abonos = Decimal(agregados['total_abonos'] or 0)
            total += saldo_base - cargos + abonos
        return total if tiene_cuentas else None

    saldo_actual_decimal = saldo_desde_cuentas([cuenta_seleccionada]) if cuenta_seleccionada else saldo_desde_cuentas(cuentas_usuario)
    if saldo_actual_decimal is None:
        ultimo_mov = movimientos_usuario.order_by('-fecha', '-id').first()
        saldo_actual_decimal = Decimal(ultimo_mov.saldo) if ultimo_mov and ultimo_mov.saldo is not None else Decimal('0')
    saldo_actual = saldo_actual_decimal

    saldo_resumen = saldo_desde_cuentas([cuenta_seleccionada], fecha_limite=inicio) if cuenta_seleccionada else saldo_desde_cuentas(cuentas_usuario, fecha_limite=inicio)

    # Totales del mes
    movimientos_rango = movimientos_usuario.filter(fecha__gte=inicio, fecha__lte=fin)
    total_abonos_mes = movimientos_rango.aggregate(total=Sum('abono'))['total'] or 0
    total_cargos_mes = movimientos_rango.aggregate(total=Sum('cargo'))['total'] or 0

    dias_periodo = max(1, (fin - inicio).days + 1)
    gasto_promedio_diario = float(total_cargos_mes) / dias_periodo if total_cargos_mes else 0
    ingreso_promedio_diario = float(total_abonos_mes) / dias_periodo if total_abonos_mes else 0

    inicio_mes_actual = inicio.replace(day=1)
    prev_fin = inicio_mes_actual - timedelta(days=1)
    prev_inicio = prev_fin.replace(day=1)
    prev_mov = movimientos_usuario.filter(fecha__range=(prev_inicio, prev_fin)).order_by('-fecha', '-id').first()
    saldo_prev = Decimal(prev_mov.saldo) if prev_mov and prev_mov.saldo is not None else Decimal(0)
    delta_vs_prev = float(saldo_actual - saldo_prev)
    delta_porcentaje = (delta_vs_prev / float(saldo_prev) * 100) if saldo_prev else None

    # Saldo actual (último registro por fecha e id)
    saldo_actual = saldo_actual_decimal

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

    monthly_qs = list(
        movimientos_usuario
        .annotate(month=TruncMonth('fecha'))
        .values('month')
        .order_by('month')
        .annotate(total_abonos=Sum('abono'), total_cargos=Sum('cargo'))
    )
    if len(monthly_qs) > 12:
        monthly_qs = monthly_qs[-12:]
    monthly_labels = [m['month'].strftime('%b %Y') if m['month'] else '' for m in monthly_qs]
    monthly_abonos = [float(m['total_abonos'] or 0) for m in monthly_qs]
    monthly_cargos = [float(m['total_cargos'] or 0) for m in monthly_qs]

    categoria_qs = list(
        movimientos_rango
        .filter(cargo__gt=0)
        .values('categoria__nombre', 'categoria__color')
        .annotate(total=Sum('cargo'))
        .order_by('-total')
    )
    months_period = movimientos_rango.annotate(month=TruncMonth('fecha')).values_list('month', flat=True).distinct()
    months_count = max(1, len([m for m in months_period if m is not None]))
    pie_labels = []
    pie_values = []
    pie_colors = []
    for item in categoria_qs:
        pie_labels.append(item['categoria__nombre'] or 'Sin categoría')
        pie_values.append(float(item['total'] or 0))
        pie_colors.append(item['categoria__color'] or '#94a3b8')
    avg_labels = pie_labels[:]
    avg_values = [
        round((float(item['total'] or 0) / months_count), 2)
        for item in categoria_qs
    ]

    # Saldo acumulado diario: parte del saldo previo a la fecha de inicio
    if saldo_resumen is None:
        previo = movimientos_usuario.filter(fecha__lt=inicio).order_by('-fecha', '-id').first()
        saldo_resumen = Decimal(previo.saldo) if previo and previo.saldo is not None else Decimal('0')
    acumulado = float(saldo_resumen)
    serie_saldo = []
    for f in fechas:
        acumulado += float(mapa_abonos.get(f, 0) or 0) - float(mapa_cargos.get(f, 0) or 0)
        serie_saldo.append(acumulado)

    if cuenta_seleccionada:
        cuenta_resumen = f"{cuenta_seleccionada.nombre_identificador} · {cuenta_seleccionada.banco}"
    else:
        cuenta_resumen = "Todas las cuentas" if cuentas_usuario.exists() else "Todos tus movimientos"

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
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_abonos_json': json.dumps(monthly_abonos),
        'monthly_cargos_json': json.dumps(monthly_cargos),
        'pie_labels_json': json.dumps(pie_labels),
        'pie_values_json': json.dumps(pie_values),
        'pie_colors_json': json.dumps(pie_colors),
        'avg_labels_json': json.dumps(avg_labels),
        'avg_values_json': json.dumps(avg_values),
        'gasto_promedio_diario': gasto_promedio_diario,
        'delta_vs_prev': delta_vs_prev,
        'delta_porcentaje': delta_porcentaje,
        'dias_periodo': dias_periodo,
        'ingreso_promedio_diario': ingreso_promedio_diario,
        'saldo_prev': float(saldo_prev),
        'cuentas_usuario': cuentas_usuario,
        'cuenta_actual': cuenta_param,
        'cuenta_resumen': cuenta_resumen,
        'cuenta_seleccionada': cuenta_seleccionada,
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
    

# --- CUENTAS BANCARIAS ---
@login_required
def cuentas_list(request):
    cuentas = CuentaBanco.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'cuentas_list.html', {'cuentas': cuentas})


@login_required
def cuentas_create(request):
    if request.method == 'POST':
        form = CuentaBancoForm(request.POST)
        if form.is_valid():
            cuenta = form.save(commit=False)
            cuenta.usuario = request.user
            cuenta.save()
            messages.success(request, 'La cuenta bancaria se creó correctamente.')
            return redirect('cuentas_list')
        messages.error(request, 'Revisa los campos destacados e intenta nuevamente.')
    else:
        form = CuentaBancoForm()
    return render(request, 'cuentas_create.html', {'form': form})


@login_required
def cuentas_edit(request, pk):
    cuenta = get_object_or_404(CuentaBanco, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = CuentaBancoForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Actualizaste la cuenta bancaria.')
            return redirect('cuentas_list')
        messages.error(request, 'Revisa la información ingresada e intenta nuevamente.')
    else:
        form = CuentaBancoForm(instance=cuenta)
    return render(request, 'cuentas_edit.html', {'form': form, 'cuenta': cuenta})


@login_required
def cuentas_delete(request, pk):
    cuenta = get_object_or_404(CuentaBanco, pk=pk, usuario=request.user)
    if request.method == 'POST':
        cuenta.delete()
        messages.success(request, 'La cuenta bancaria se eliminó correctamente.')
        return redirect('cuentas_list')
    return render(request, 'cuentas_delete.html', {'cuenta': cuenta})


# --- CATEGORÍAS ---
@login_required
def categorias_list(request):
    categorias = CategoriaGasto.objects.filter(usuario=request.user).order_by('nombre')
    return render(request, 'categorias_list.html', {'categorias': categorias})


@login_required
def categorias_create(request):
    if request.method == 'POST':
        form = CategoriaGastoForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()
            messages.success(request, 'La categoría se creó correctamente.')
            return redirect('categorias_list')
        messages.error(request, 'Revisa los campos resaltados e intenta nuevamente.')
    else:
        form = CategoriaGastoForm()
    return render(request, 'categorias_create.html', {'form': form})


@login_required
def categorias_edit(request, pk):
    categoria = get_object_or_404(CategoriaGasto, pk=pk, usuario=request.user)
    if request.method == 'POST':
        form = CategoriaGastoForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'La categoría se actualizó correctamente.')
            return redirect('categorias_list')
        messages.error(request, 'Revisa los campos resaltados e intenta nuevamente.')
    else:
        form = CategoriaGastoForm(instance=categoria)
    return render(request, 'categorias_edit.html', {'form': form, 'categoria': categoria})


@login_required
def categorias_delete(request, pk):
    categoria = get_object_or_404(CategoriaGasto, pk=pk, usuario=request.user)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'La categoría se eliminó correctamente.')
        return redirect('categorias_list')
    return render(request, 'categorias_delete.html', {'categoria': categoria})

    
@login_required
def subir_cartola(request):
    cuentas = CuentaBanco.objects.filter(usuario=request.user).order_by('-fecha_creacion')

    if request.method == "POST":
        cuenta_id = request.POST.get("cuenta_id")
        if not cuenta_id:
            messages.error(request, "Selecciona la cuenta a la que pertenece la cartola.")
            return redirect("subir_cartola")

        cuenta = get_object_or_404(CuentaBanco, pk=cuenta_id, usuario=request.user)

        if not request.FILES.get("archivo_excel"):
            messages.error(request, "Debes adjuntar un archivo Excel para continuar.")
            return redirect("subir_cartola")

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

        def limpiar_monto(valor):
            if valor is None or (not isinstance(valor, str) and pd.isna(valor)):
                return 0.0
            if isinstance(valor, (int, float, Decimal)):
                return float(valor)
            texto = str(valor).strip()
            if not texto:
                return 0.0
            signos = ['$', 'CLP', 'USD', '€', 'EUR']
            for signo in signos:
                texto = texto.replace(signo, '')
            texto = (texto.replace('\xa0', '')
                           .replace(' ', '')
                           .replace('\t', '')
                           .replace('\u202f', ''))
            if texto.startswith('(') and texto.endswith(')'):
                texto = '-' + texto[1:-1]
            if texto.count(',') == 1 and texto.count('.') > 1:
                texto = texto.replace('.', '')
            if texto.count(',') == 1 and texto.count('.') == 0:
                texto = texto.replace(',', '.')
            elif texto.count('.') > 1 and texto.count(',') == 0:
                parts = texto.split('.')
                texto = ''.join(parts[:-1]) + '.' + parts[-1]
            else:
                texto = texto.replace('.', '').replace(',', '.')
            try:
                return float(texto)
            except ValueError:
                texto = ''.join(ch for ch in texto if (ch.isdigit() or ch in '-.'))
                return float(texto or 0)

        try:
            # Detectar motor según extensión
            if archivo.name.endswith(".xlsx"):
                df = pd.read_excel(ruta_archivo, engine="openpyxl")
            elif archivo.name.endswith(".xls"):
                df = pd.read_excel(ruta_archivo, engine="xlrd")
            else:
                raise ValueError("Formato no soportado. Usa .xls o .xlsx")

            # Normalizar encabezados
            columna_normalizada = {col: col.strip().title() for col in df.columns}
            df.rename(columns=columna_normalizada, inplace=True)

            # Aceptar “Cargo/Abono” o “Cargos/Abonos”
            if 'Cargo' in df.columns and 'Cargos' not in df.columns:
                df.rename(columns={'Cargo': 'Cargos'}, inplace=True)
            if 'Abono' in df.columns and 'Abonos' not in df.columns:
                df.rename(columns={'Abono': 'Abonos'}, inplace=True)

            columnas_requeridas = {'Fecha', 'Descripcion', 'Cargos', 'Abonos'}
            columnas_presentes = set(df.columns)

            if not columnas_requeridas.issubset(columnas_presentes):
                messages.error(
                    request,
                    "El archivo debe contener las columnas: Fecha, Descripcion, Cargos y Abonos."
                )
                return redirect("subir_cartola")

            ultimo_movimiento = cuenta.movimientos.order_by('-fecha', '-id').first()
            saldo_actual = float(ultimo_movimiento.saldo) if ultimo_movimiento and ultimo_movimiento.saldo is not None else float(cuenta.saldo_inicial)

            #  Procesar filas
            registros_creados = 0
            for _, fila in df.iterrows():
                try:
                    fecha_val = pd.to_datetime(fila['Fecha'], dayfirst=True, errors='coerce')
                    if pd.isna(fecha_val):
                        raise ValueError("Fecha inválida")
                    fecha = fecha_val.date()
                    descripcion = str(fila['Descripcion']).strip()
                    cargo = limpiar_monto(fila.get('Cargos'))
                    abono = limpiar_monto(fila.get('Abonos'))

                    saldo_final = saldo_actual - cargo + abono
                    saldo_actual = saldo_final

                    Movimiento.objects.create(
                        usuario=request.user,
                        cuenta=cuenta,
                        fecha=fecha,
                        descripcion=descripcion,
                        cargo=cargo,
                        abono=abono,
                        saldo=saldo_final,
                        archivo_origen=archivo.name
                    )
                    registros_creados += 1
                except Exception as fila_error:
                    print(f" Error en fila: {fila_error}")
                    continue

            messages.success(
                request,
                f"Archivo '{archivo.name}' cargado correctamente. {registros_creados} movimientos registrados para {cuenta.nombre_identificador}."
            )
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {str(e)}")
            print("Error procesando Excel:", e)

            return redirect("subir_cartola")

        return redirect("clasificar_movimientos", cuenta_id=cuenta.id, archivo=archivo.name)

    return render(request, "subir_cartola.html", {'cuentas': cuentas})


@login_required
def clasificar_movimientos(request, cuenta_id, archivo):
    cuenta = get_object_or_404(CuentaBanco, pk=cuenta_id, usuario=request.user)
    movimientos_query = Movimiento.objects.filter(
        usuario=request.user,
        cuenta=cuenta,
        archivo_origen=archivo
    ).order_by('-fecha', '-id')

    if not movimientos_query.exists():
        messages.info(request, 'No se encontraron movimientos para clasificar.')
        return redirect('pagina_principal')

    paginator = Paginator(movimientos_query, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categorias = CategoriaGasto.objects.filter(usuario=request.user).order_by('nombre')
    clasificados = movimientos_query.filter(categoria__isnull=False).count()
    total = movimientos_query.count()

    context = {
        'cuenta': cuenta,
        'archivo': archivo,
        'page_obj': page_obj,
        'categorias': categorias,
        'clasificados': clasificados,
        'total_movimientos': total,
    }
    return render(request, 'clasificar_movimientos.html', context)


@login_required
def guardar_categorias(request):
    if request.method != 'POST':
        messages.error(request, 'Acción inválida.')
        return redirect('pagina_principal')

    movimiento_ids = request.POST.getlist('movimiento_id')
    ids_validos = []
    for valor in movimiento_ids:
        try:
            ids_validos.append(int(valor))
        except (TypeError, ValueError):
            continue
    if not ids_validos:
        messages.warning(request, 'No se enviaron movimientos para clasificar.')
        return redirect('pagina_principal')

    movimientos = Movimiento.objects.filter(id__in=ids_validos, usuario=request.user)
    categorias_disponibles = {
        str(cat.id): cat for cat in CategoriaGasto.objects.filter(usuario=request.user)
    }

    actualizados = 0
    for movimiento in movimientos:
        categoria_id = request.POST.get(f'categoria_{movimiento.id}')
        if not categoria_id:
            if movimiento.categoria_id is not None:
                movimiento.categoria = None
                movimiento.save(update_fields=['categoria'])
                actualizados += 1
            continue

        categoria = categorias_disponibles.get(categoria_id)
        if not categoria:
            continue
        if movimiento.categoria_id != categoria.id:
            movimiento.categoria = categoria
            movimiento.save(update_fields=['categoria'])
            actualizados += 1

    messages.success(request, f"Se han clasificado correctamente {actualizados} movimientos.")
    return redirect('pagina_principal')


@login_required
def movimientos(request):
    hoy = date.today()
    cuentas_usuario = CuentaBanco.objects.filter(usuario=request.user).order_by('nombre_identificador')
    cuenta_param = request.GET.get('cuenta', 'todas')

    base_movimientos = Movimiento.objects.filter(usuario=request.user)
    if cuenta_param != 'todas':
        try:
            cuenta_obj = cuentas_usuario.get(pk=int(cuenta_param))
            base_movimientos = base_movimientos.filter(cuenta=cuenta_obj)
            cuenta_param = str(cuenta_obj.pk)
        except (ValueError, CuentaBanco.DoesNotExist):
            cuenta_param = 'todas'

    rangos = base_movimientos.aggregate(min_fecha=Min('fecha'), max_fecha=Max('fecha'))
    fecha_min = rangos['min_fecha'] or hoy.replace(day=1)
    fecha_max = rangos['max_fecha'] or hoy

    def parse_param(valor, fallback):
        if not valor:
            return fallback
        for fmt in ('%d-%m-%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(valor, fmt).date()
            except ValueError:
                continue
        return fallback

    inicio = parse_param(request.GET.get('inicio'), fecha_min)
    fin = parse_param(request.GET.get('fin'), fecha_max)
    if fin < inicio:
        inicio, fin = fin, inicio

    movimientos_query = base_movimientos.filter(
        fecha__gte=inicio,
        fecha__lte=fin
    ).order_by('-fecha', '-id')

    movimientos_sin_categoria = movimientos_query.filter(categoria__isnull=True)
    movimientos_categorizados = movimientos_query.filter(categoria__isnull=False)
    categorias = CategoriaGasto.objects.filter(usuario=request.user).order_by('nombre')

    contexto = {
        'movimientos_sin_categoria': movimientos_sin_categoria,
        'movimientos_categorizados': movimientos_categorizados,
        'categorias': categorias,
        'cuentas_usuario': cuentas_usuario,
        'cuenta_actual': cuenta_param,
        'inicio': inicio,
        'fin': fin,
        'total_movimientos': movimientos_query.count(),
        'sin_categoria_total': movimientos_sin_categoria.count(),
    }
    return render(request, 'movimientos.html', contexto)


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



