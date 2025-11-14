from django.db import models
from django.contrib.auth.models import User

DEFAULT_PROFILE_IMAGE = 'perfiles/default.png'


class CuentaBanco(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cuentas_bancarias')
    numero_cuenta = models.CharField(max_length=30)
    banco = models.CharField(max_length=100)
    nombre_identificador = models.CharField(max_length=150)
    saldo_inicial = models.DecimalField(max_digits=14, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre_identificador} - {self.banco}"


class CategoriaGasto(models.Model):
    TIPO_CHOICES = [
        ('Ingreso', 'Ingreso'),
        ('Gasto', 'Gasto'),
        ('Transferencia', 'Transferencia'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    color = models.CharField(max_length=20, default='#2563eb')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        unique_together = ('usuario', 'nombre')

    def __str__(self):
        return self.nombre


class Movimiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cuenta = models.ForeignKey(CuentaBanco, on_delete=models.CASCADE, related_name='movimientos', null=True, blank=True)
    categoria = models.ForeignKey(CategoriaGasto, on_delete=models.SET_NULL, null=True, blank=True, related_name='movimientos')
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    cargo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    abono = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    archivo_origen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha} | {self.descripcion} | Saldo: ${self.saldo}"
    

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rut = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='perfiles/',
        default=DEFAULT_PROFILE_IMAGE,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.username
