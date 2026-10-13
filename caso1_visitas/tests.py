from datetime import date, datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Persona, Visita


class DatosAdministradosVisiblesTests(TestCase):
    def setUp(self):
        self.persona = Persona.objects.create(
            rut="12345678-5",
            nombre="Ana",
            apellido="Pérez",
        )
        self.visita = Visita.objects.create(
            persona=self.persona,
            motivo_visita="Reunión con gerencia",
            fecha=date(2026, 10, 13),
            hora_entrada=timezone.make_aware(datetime(2026, 10, 13, 10, 30)),
        )

    def test_visita_creada_en_admin_aparece_en_listado_publico(self):
        response = self.client.get(reverse("visita_list"))

        self.assertContains(response, "Ana")
        self.assertContains(response, "Pérez")
        self.assertContains(response, "Reunión con gerencia")
        self.assertEqual(response["Cache-Control"], "max-age=0, no-cache, no-store, must-revalidate, private")

    def test_cambios_de_persona_administrada_aparecen_en_detalle(self):
        self.persona.nombre = "Beatriz"
        self.persona.save(update_fields=["nombre"])

        response = self.client.get(
            reverse("visita_detail", kwargs={"pk": self.visita.pk})
        )

        self.assertContains(response, "Beatriz")
        self.assertNotContains(response, "Ana")