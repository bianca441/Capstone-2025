from django.conf import settings
from django.templatetags.static import static

from .models import Perfil, DEFAULT_PROFILE_IMAGE


def profile_context(request):
    """
    Expone el perfil del usuario autenticado y una URL de avatar reutilizable.
    """
    perfil = None
    default_media_avatar = f"{settings.MEDIA_URL}{DEFAULT_PROFILE_IMAGE}"
    avatar_url = static('img/avatar-placeholder.png')

    if request.user.is_authenticated:
        perfil, _ = Perfil.objects.get_or_create(user=request.user)
        # Asegura que request.user siempre tenga el atributo perfil disponible.
        if not hasattr(request.user, 'perfil'):
            request.user.perfil = perfil

        if perfil.profile_image and perfil.profile_image.name != DEFAULT_PROFILE_IMAGE:
            try:
                avatar_url = perfil.profile_image.url
            except ValueError:
                avatar_url = default_media_avatar
        else:
            avatar_url = default_media_avatar

    return {
        'perfil_global': perfil,
        'profile_avatar_url': avatar_url,
        'default_avatar_url': default_media_avatar,
    }
