from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        # Importa señales para crear perfiles automáticamente.
        from . import signals  # noqa: F401
