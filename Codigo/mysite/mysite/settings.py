from pathlib import Path
import os

# --- BASE DIR ---
BASE_DIR = Path(__file__).resolve().parent.parent


# --- SEGURIDAD ---
SECRET_KEY = 'django-insecure-x_^%@zssl7i#8sp$2e^j$_ydw^#x)&p(0ydcj&$1mr)r1)w*i_'
DEBUG = True
ALLOWED_HOSTS = []


# --- APLICACIONES INSTALADAS ---
INSTALLED_APPS = [
    # Aplicaciones del núcleo Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicación principal
    'main',
]


# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
            BASE_DIR / 'main' / 'templates',  # ✅ ruta central de tus HTML
        ],

        # También buscará dentro de cada app registrada (app_name/templates)
        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# --- APLICACIÓN WSGI ---
WSGI_APPLICATION = 'mysite.wsgi.application'


# --- BASE DE DATOS ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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