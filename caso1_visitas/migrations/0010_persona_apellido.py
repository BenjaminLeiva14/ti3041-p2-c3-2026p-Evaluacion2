import caso1_visitas.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("caso1_visitas", "0009_persona_visita_persona"),
    ]

    operations = [
        migrations.AddField(
            model_name="persona",
            name="apellido",
            field=models.CharField(
                default="Pendiente",
                max_length=50,
                validators=[caso1_visitas.validators.validar_nombre],
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="persona",
            name="nombre",
            field=models.CharField(
                max_length=50,
                validators=[caso1_visitas.validators.validar_nombre],
            ),
        ),
    ]
