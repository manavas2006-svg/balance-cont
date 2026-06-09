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
        #si tiene cuentas hijas busca sus saldos y los suma
        if self.hijos.exists():
            return sum(hijo.obtener_saldo(fecha_inicio, fecha_fin) for i, hijo in enumerate(self.hijos.all()))
        
        # si es cuenta detalle busca sus movimiento 
        movimientos = self.movimientos.all()
        
        # filtros de fecha para los estados financieros por mes/año
        if fecha_inicio:
            movimientos = movimientos.filter(asiento__fecha__gte=fecha_inicio)
        if fecha_fin:
            movimientos = movimientos.filter(asiento__fecha__lte=fecha_fin)
            
        total_debe = sum(m.debe for m in movimientos)
        total_haber = sum(m.haber for m in movimientos)
        
        # El saldo depende de la naturaleza
        if self.naturaleza == 'DEU':
            return total_debe - total_haber
        else:
            return total_haber - total_debe
        
def clean(self):
        """
        Evita ciclos infinitos en la jerarquía del Plan de Cuentas.
        """
        super().clean()
        
        if self.padre == self:
            raise ValidationError("Una cuenta no puede ser padre de sí misma.")
        
        comprobacion_padre = self.padre
        while comprobacion_padre is not None:
            if comprobacion_padre == self:
                raise ValidationError(
                    f"Ciclo infinito detectado. La cuenta '{self.nombre}' "
                    f"no puede tener como ancestro a una de sus propias cuentas hijas."
                )
            comprobacion_padre = comprobacion_padre.padre

class AsientoCabecera(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name="Nro. Asiento")
    fecha = models.DateField(verbose_name="Fecha")
    descripcion = models.TextField(verbose_name="Descripción del Asiento")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Libro Diario"
        ordering = ['-fecha', 'codigo']

    def __str__(self):
        return f"Asiento {self.codigo} - {self.fecha}"

    def clean(self):
        """
        El Guardián del Balance: Valida las reglas de la partida doble 
        antes de que el asiento se guarde en la base de datos.
        """
        super().clean()
        
        if self.pk:
            detalles = self.detalles.all()
            if detalles.exists():
                total_debe = sum(d.debe for d in detalles)
                total_haber = sum(d.haber for d in detalles)
                
                # Debe es igual a Haber
                if total_debe != total_haber:
                    raise ValidationError(
                        f"¡Asiento Descuadrado! El total del Debe ({total_debe}) "
                        f"debe ser igual al total del Haber ({total_haber}). "
                        f"Diferencia: {abs(total_debe - total_haber)}"
                    )
                
class AsientoDetalle(models.Model):
    asiento = models.ForeignKey(
        AsientoCabecera, 
        on_delete=models.CASCADE, 
        related_name='detalles', 
        verbose_name="Asiento"
    )
    cuenta = models.ForeignKey(
        Cuenta, 
        on_delete=models.PROTECT, 
        related_name='movimientos', 
        verbose_name="Cuenta"
    )

    debe = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Debe")
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Haber")

    class Meta:
        verbose_name = "Detalle de Asiento"
        verbose_name_plural = "Detalles de Asiento"

    def __str__(self):
        return f"{self.cuenta.nombre} | Debe: {self.debe} | Haber: {self.haber}"

    def clean(self):
        """
        Validación a nivel de línea: No permite registrar transacciones
        en cuentas que tengan hijos (cuentas que no sean detalle).
        """
        super().clean()
        if self.cuenta.hijos.exists():
            raise ValidationError(
                f"La cuenta '{self.cuenta.nombre}' es una cuenta de grupo y no puede tener movimientos directos. "
                f"Solo puedes registrar movimientos en cuentas de último nivel (Cuentas Detalle)."
            )
       