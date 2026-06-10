from django.urls import path
from . import views

urlpatterns = [
    path('api/balance/', views.api_balance_comprobacion, name='api_balance_comprobacion'),
    path('plan/', views.plan_cuentas_view, name='plan_cuentas'),
    path('diario/', views.libro_diario_view, name='libro_diario'),
]