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