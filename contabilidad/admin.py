from django.contrib import admin
from django.contrib import admin
from .models import Cuenta

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    
    list_display = ('codigo', 'nombre', 'tipo', 'naturaleza', 'padre')
    search_fields = ('codigo', 'nombre')
    list_filter = ('tipo', 'naturaleza')
    fields = ('codigo', 'nombre', 'tipo', 'naturaleza', 'padre')
    from django.contrib import admin
from .models import Cuenta, AsientoCabecera, AsientoDetalle

class AsientoDetalleInline(admin.TabularInline):
    model = AsientoDetalle
    extra = 2 
    fields = ('cuenta', 'debe', 'haber')

@admin.register(AsientoCabecera)
class AsientoCabeceraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'fecha', 'descripcion')
    search_fields = ('codigo', 'descripcion')
    list_filter = ('fecha',)
    inlines = [AsientoDetalleInline]