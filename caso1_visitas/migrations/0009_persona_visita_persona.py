import caso1_visitas.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


def calcular_digito_verificador(rut):
    total = 0
    factor = 2

    for digit in reversed(str(rut)):
        total += int(digit) * factor
        factor = 2 if factor == 7 else factor + 1

    resto = 11 - (total % 11)
    if resto == 11:
        return "0"
    if resto == 10:
        return "K"
    return str(resto)


def formatear_rut(rut):
    return f"{int(rut)}-{calcular_digito_verificador(rut)}"


def forwards(apps, schema_editor):
    Persona = apps.get_model("caso1_visitas", "Persona")
    Visita = apps.get_model("caso1_visitas", "Visita")

    for visita in Visita.objects.all().iterator():
        rut = formatear_rut(visita.rut)
        persona, _ = Persona.objects.get_or_create(
            rut=rut,
            defaults={"nombre": visita.nombre},
        )
        visita.persona_id = persona.rut
        visita.save(update_fields=["persona"])


def backwards(apps, schema_editor):
    Persona = apps.get_model("caso1_visitas", "Persona")
    Visita = apps.get_model("caso1_visitas", "Visita")

    for visita in Visita.objects.all().iterator():
        persona = Persona.objects.get(rut=visita.persona_id)
        visita.rut = int(persona.rut.split("-")[0])
        visita.nombre = persona.nombre
        visita.save(update_fields=["rut", "nombre"])


class Migration(migrations.Migration):

    dependencies = [
        ("caso1_visitas", "0008_visita_hora_salida_and_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Persona",
            fields=[
                (
                    "rut",
                    models.CharField(
                        max_length=11,
                        primary_key=True,
                        serialize=False,
                        validators=[
                            django.core.validators.MinLengthValidator(9),
                            django.core.validators.MaxLengthValidator(11),
                            caso1_visitas.validators.validar_rut,
                        ],
                        verbose_name="RUT",
                    ),
                ),
                ("nombre", models.CharField(max_length=15)),
            ],
        ),
        migrations.AddField(
            model_name="visita",
            name="persona",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="visitas",
                to="caso1_visitas.persona",
            ),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.RemoveField(
            model_name="visita",
            name="nombre",
        ),
        migrations.RemoveField(
            model_name="visita",
            name="rut",
        ),
        migrations.AlterField(
            model_name="visita",
            name="persona",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="visitas",
                to="caso1_visitas.persona",
            ),
        ),
    ]
