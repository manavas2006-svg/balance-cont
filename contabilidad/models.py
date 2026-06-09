from django.db import models

from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal

class Cuenta(models.Model):
    TIPO_CHOICES = [
        ('ACT', 'Activo'),
        ('PAS', 'Pasivo'),
        ('PAT', 'Patrimonio'),
        ('ING', 'Ingreso'),
        ('EGR', 'Egreso'),
    ]
    
    NATURALEZA_CHOICES = [
        ('DEU', 'Deudora'),
        ('ACR', 'Acreedora'),
    ]

    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código Contable")
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Cuenta")
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES, verbose_name="Tipo de Cuenta")
    naturaleza = models.CharField(max_length=3, choices=NATURALEZA_CHOICES, verbose_name="Naturaleza")
    
    # con self se apunta a sí misma
    # si 'padre' es null, significa que es una cuenta raíz osea la primera cuenta, si no es null, entonces es una cuenta hija de otra cuenta
    padre = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='hijos',
        verbose_name="Cuenta Padre"
    )

    class Meta:
        verbose_name = "Cuenta"
        verbose_name_plural = "Plan de Cuentas"
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def obtener_saldo(self, fecha_inicio=None, fecha_fin=None):
        """
        metodo recursivo  si la cuenta tiene hijas, suma los saldos 
        de las hijas si es una cuenta de detalle (hoja) calcula sus movimientos.
        """
        
        if self.hijos.exists():
            return sum(hijo.obtener_saldo(fecha_inicio, fecha_fin) for hijo in self.hijos.all())
        
        # Si es una cuenta detalle (sin hijos), calculamos el saldo según sus movimientos
      
        return Decimal('0.00')
