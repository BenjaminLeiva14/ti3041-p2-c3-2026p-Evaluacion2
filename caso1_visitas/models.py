# Dependencias y validadores de los modelos.
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models
from datetime import date

from .validators import validar_nombre, validar_rut


# Persona identificada de forma única por su RUT.
class Persona(models.Model):
    rut = models.CharField(
        max_length=11,
        primary_key=True,
        validators=[
            MinLengthValidator(9),
            MaxLengthValidator(11),
            validar_rut,
        ],
        verbose_name="RUT",
    )
    nombre = models.CharField(max_length=50, validators=[validar_nombre])
    apellido = models.CharField(max_length=50, validators=[validar_nombre])

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    # Representación legible para el Admin y relaciones.
    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"


# Registro de una visita asociada a una persona.
class Visita(models.Model):
    persona = models.ForeignKey(
        Persona,
        on_delete=models.PROTECT,
        related_name="visitas",
    )
    motivo_visita = models.CharField(max_length=320)
    fecha = models.DateField(default=date.today, verbose_name="Fecha")
    hora_entrada = models.DateTimeField()
    hora_salida = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Hora de salida",
    )
    """@property = decorador que permite convertir un método de una clase en un atributo de solo lectura (o gestionado), permitiendo acceder a él con la notación de punto (objeto.atributo) sin usar paréntesis (()), mientras ejecuta código por detrás."""

    @property
    def nombre(self):
        return self.persona.nombre_completo

    @property
    def apellido(self):
        return self.persona.apellido

    @property
    def rut(self):
        return self.persona.rut

    @property
    def esta_dentro(self):
        return self.hora_salida is None

    # Reglas de consistencia temporal para entrada y salida.
    def clean(self):
        super().clean()
        errors = {}
        if self.fecha and self.hora_entrada:
            entrada_fecha = self.hora_entrada.date()
            if entrada_fecha < self.fecha:
                errors["hora_entrada"] = (
                    "La fecha de entrada no puede ser anterior a la fecha solicitada."
                )
        if self.hora_salida and self.hora_entrada:
            if self.hora_salida < self.hora_entrada:
                errors["hora_salida"] = (
                    "La hora de salida no puede ser anterior a la hora de entrada."
                )
        if errors:
            raise ValidationError(errors)

    # Representación legible del registro de visita.
    def __str__(self):
        return f"{self.persona} - {self.fecha}"
