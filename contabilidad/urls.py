from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views  
from . import views

urlpatterns = [
    path('diario/', views.libro_diario_view, name='libro_diario'),
    path('plan/', views.plan_cuentas_view, name='plan_cuentas'),
    path('balance/comprobacion/', views.api_balance_comprobacion, name='api_balance'),
    path('usuarios/', views.gestion_usuarios_view, name='gestion_usuarios'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('logged-out/', TemplateView.as_view(template_name='Registro/sesion_cerrada.html'), name='sesion_cerrada'),
]