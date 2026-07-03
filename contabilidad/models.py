from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

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

    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=3, choices=TIPO_CHOICES)
    naturaleza = models.CharField(max_length=3, choices=NATURALEZA_CHOICES)
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='hijos')

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class AsientoCabecera(models.Model):
    codigo = models.CharField(max_length=5, unique=True)
    fecha = models.DateField()
    descripcion = models.TextField()
    
   
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='asientos'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Asiento {self.codigo} - {self.fecha}"


class AsientoDetalle(models.Model):
    asiento = models.ForeignKey(AsientoCabecera, on_delete=models.CASCADE, related_name='detalles')
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name='detalles')
    
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Detalle de {self.asiento.codigo} - Cuenta {self.cuenta.codigo}"

class Perfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username} - Cédula: {self.cedula}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def verificar_o_crear_perfil(sender, instance, created, **kwargs):
    if created:
        try:
            if hasattr(instance, 'perfil'):
                return
            Perfil.objects.create(usuario=instance, cedula=f"V-TEMP-{instance.id}")
        except Exception:
            pass

  