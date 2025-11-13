from django.db import models
from django.contrib.auth.models import User

class Movimiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)

    def __str__(self):
        return self.user.username
