from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('cambio-clave/', views.cambio_clave, name='cambio_clave'),
    path('principal/', views.pagina_principal, name='pagina_principal'),
    path('logout/', views.logout_view, name='logout'),
    path('cuentas/', views.cuentas_list, name='cuentas_list'),
    path('cuentas/nueva/', views.cuentas_create, name='cuentas_create'),
    path('cuentas/<int:pk>/editar/', views.cuentas_edit, name='cuentas_edit'),
    path('cuentas/<int:pk>/eliminar/', views.cuentas_delete, name='cuentas_delete'),
    path('categorias/', views.categorias_list, name='categorias_list'),
    path('categorias/nueva/', views.categorias_create, name='categorias_create'),
    path('categorias/<int:pk>/editar/', views.categorias_edit, name='categorias_edit'),
    path('categorias/<int:pk>/eliminar/', views.categorias_delete, name='categorias_delete'),
    path('subir-cartola/', views.subir_cartola, name='subir_cartola'),
    path('clasificar-movimientos/<int:cuenta_id>/<str:archivo>/', views.clasificar_movimientos, name='clasificar_movimientos'),
    path('guardar-categorias/', views.guardar_categorias, name='guardar_categorias'),
    path('movimientos/', views.movimientos, name='movimientos'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),
]
