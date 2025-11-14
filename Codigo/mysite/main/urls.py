from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('cambio-clave/', views.cambio_clave, name='cambio_clave'),
    path('principal/', views.pagina_principal, name='pagina_principal'),
    path('logout/', views.logout_view, name='logout'),
    path('subir-cartola/', views.subir_cartola, name='subir_cartola'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
]
