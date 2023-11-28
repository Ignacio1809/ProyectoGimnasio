from django.db import models
from django.contrib.auth.models import User
import json
# Create your models here.
#en este archivo crearemos las tablas de nuestra base de datos 


class Video(models.Model):
    url = models.URLField(unique=True)
    semana = models.IntegerField()  # Añade un campo para la semana si es necesario

    def __str__(self):
        return self.url

class Plan(models.Model):
    nombre_plan = models.CharField(max_length=20)
    descripcion = models.TextField()
    precio = models.FloatField()
    duracion = models.CharField(max_length=20)
    beneficio = models.TextField()
    informe_url = models.URLField(max_length=200, blank=True, null=True)
    # Nuevo campo para manejar el streaming
    es_streaming = models.BooleanField(default=False)
    # URL para la sesión de streaming, si es aplicable
    url_streaming = models.URLField(max_length=200, blank=True, null=True)
    videos = models.ManyToManyField(Video, blank=True)

    def __str__(self):
        return self.nombre_plan

class cliente(models.Model):
    telefono = models.CharField(max_length=9)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    estatura = models.FloatField()
    peso = models.FloatField()
    imc = models.FloatField()
    fecha_nac = models.DateField()
    passwrd = models.CharField(max_length=12)
    plan_actual = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.email

    

class Pago(models.Model):
    cliente = models.ForeignKey(cliente, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    monto = models.FloatField()
    estado = models.CharField(max_length=20)  # Ejemplos: 'Exitoso', 'Fallido', 'Pendiente'
    # Otros campos relevantes como referencia de transacción, etc.

    def __str__(self):
        return f"{self.cliente.email} - {self.plan.nombre_plan} - {self.estado}"



class VideoView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)  # Relación con el modelo Video
    viewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} viewed {self.video.url}: {self.viewed}"

class UserVideoProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'video')

    def __str__(self):
        return f"{self.user.username} - {self.video.url} - Watched: {self.watched}"
    


