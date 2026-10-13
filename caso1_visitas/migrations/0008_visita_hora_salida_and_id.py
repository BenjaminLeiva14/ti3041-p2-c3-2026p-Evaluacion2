import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("caso1_visitas", "0007_visita_fecha"),
    ]

    operations = [
        migrations.AlterField(
            model_name="visita",
            name="rut",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(70000000),
                    django.core.validators.MaxValueValidator(259999999),
                ],
            ),
        ),
        migrations.AddField(
            model_name="visita",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
        migrations.AddField(
            model_name="visita",
            name="hora_salida",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Hora de salida",
            ),
        ),
    ]
