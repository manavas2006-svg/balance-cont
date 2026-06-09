from django.contrib import admin
from django.contrib import admin
from .models import Cuenta

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    
    list_display = ('codigo', 'nombre', 'tipo', 'naturaleza', 'padre')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo', 'naturaleza')
    fields = ('codigo', 'nombre', 'tipo', 'naturaleza', 'padre')