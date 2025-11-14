import os
from pathlib import Path
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

# --- BASE DIR ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CARGAR VARIABLES DE ENTORNO ---
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path)

print("✅ Archivo .env cargado desde:", dotenv_path)
print("🔗 DATABASE_URL detectado:", os.getenv("DATABASE_URL"))

# --- SEGURIDAD ---
SECRET_KEY = 'django-insecure-x_^%@zssl7i#8sp$2e^j$_ydw^#x)&p(0ydcj&$1mr)r1)w*i_'
DEBUG = True
ALLOWED_HOSTS = []  # Puedes agregar dominios o IPs en despliegue


# --- APLICACIONES INSTALADAS ---
INSTALLED_APPS = [
    # Aplicaciones del núcleo Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Aplicación principal
    'main.apps.MainConfig',
]


# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# --- CONFIGURACIÓN DE URL PRINCIPAL ---
ROOT_URLCONF = 'mysite.urls'


# --- PLANTILLAS (TEMPLATES) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        # Rutas donde Django buscará plantillas HTML
        'DIRS': [
            BASE_DIR / 'main' / 'templates',  # ✅ carpeta principal de tus HTML
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.profile_context',
            ],
        },
    },
]


# --- APLICACIÓN WSGI ---
WSGI_APPLICATION = 'mysite.wsgi.application'


# --- BASE DE DATOS (SUPABASE) ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}


# --- VALIDACIÓN DE CONTRASEÑAS ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- INTERNACIONALIZACIÓN ---
LANGUAGE_CODE = 'es-cl'                # idioma español (Chile)
TIME_ZONE = 'America/Santiago'         # zona horaria de Chile
USE_I18N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True


# --- ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES) ---
STATIC_URL = '/static/'

# Rutas adicionales donde buscar archivos estáticos
STATICFILES_DIRS = [
    BASE_DIR / 'main' / 'app',  # ✅ contiene /css, /js, /img
]

# (Opcional) Si más adelante usas collectstatic:
# STATIC_ROOT = BASE_DIR / 'staticfiles'


# --- ARCHIVOS MEDIA (archivos subidos por el usuario) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# --- CONFIGURACIÓN DE CLAVE POR DEFECTO ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# --- SESIONES Y LOGIN ---
LOGIN_REDIRECT_URL = 'pagina_principal'   # Redirección tras iniciar sesión
LOGOUT_REDIRECT_URL = 'login'             # Redirección tras cerrar sesión
LOGIN_URL = 'login'                       # Vista de login por defecto

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# --- LOGGING OPCIONAL (para depurar base o errores de conexión) ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
