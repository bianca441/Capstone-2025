from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('cambio-clave/', views.cambio_clave, name='cambio_clave'),
    path('principal/', views.pagina_principal, name='pagina_principal'),
]