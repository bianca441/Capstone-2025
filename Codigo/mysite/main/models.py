from django.db import models
from django.contrib.auth.models import User

class Movimiento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    categoria = models.CharField(max_length=100, blank=True, null=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=[('Ingreso', 'Ingreso'), ('Gasto', 'Gasto')])
    archivo_origen = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.fecha} - {self.descripcion} ({self.monto})"