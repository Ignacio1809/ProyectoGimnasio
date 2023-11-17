from django.db import models

# Create your models here.
#en este archivo crearemos las tablas de nuestra base de datos 


class Plan(models.Model):
    nombre_plan = models.CharField(max_length=20)
    descripcion = models.TextField()
    precio = models.FloatField()
    duracion =  models.CharField(max_length=20)
    beneficio= models.TextField()
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
