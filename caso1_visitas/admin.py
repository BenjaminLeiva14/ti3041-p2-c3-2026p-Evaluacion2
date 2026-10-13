# Dependencias del panel administrativo y sus mensajes.
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone

from .models import Persona, Visita
from .validators import normalizar_rut, validar_nombre


# Identidad visible en el encabezado y el título del panel administrativo.
admin.site.site_header = "Recepción & visitas"
admin.site.site_title = "Recepción & visitas"
admin.site.index_title = "Panel de control de visitas"


# Acción masiva para registrar la salida de visitas pendientes.
@admin.action(description="Marcar salida de las visitas seleccionadas")
def marcar_salida(modeladmin, request, queryset):
    visitas_pendientes = queryset.filter(hora_salida__isnull=True)
    actualizadas = visitas_pendientes.update(hora_salida=timezone.now())

    if actualizadas:
        modeladmin.message_user(
            request,
            f"Se marcó la salida de {actualizadas} visita(s).",
            messages.SUCCESS,
        )
    else:
        modeladmin.message_user(
            request,
            "Las visitas seleccionadas ya tienen registrada su salida.",
            messages.WARNING,
        )


# Formulario administrativo con las mismas reglas de nombres.
class PersonaAdminForm(forms.ModelForm):
    nombre = forms.CharField(
        max_length=50,
        strip=False,
        validators=[validar_nombre],
    )
    apellido = forms.CharField(
        max_length=50,
        strip=False,
        validators=[validar_nombre],
    )

    class Meta:
        model = Persona
        fields = "__all__"


# Administración de personas, búsquedas y cantidad de visitas.
@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    form = PersonaAdminForm
    list_display = ("rut", "nombre_completo", "cantidad_visitas") # muestra la lista con las variables ingresadas
    search_fields = ("rut", "nombre", "apellido") # Busqueda por rut, nombre y apellido
    ordering = ("rut",) # Ordena por rut
    list_per_page = 25

    # El RUT no cambia después de crear una persona relacionada.
    def get_readonly_fields(self, request, obj=None):
        # El RUT identifica a la persona y no debe cambiarse después de crearla.
        return ("rut",) if obj else ()

    @admin.display(description="Visitas")
    def cantidad_visitas(self, obj):
        return obj.visitas.count()

    @admin.display(description="Nombre completo")
    def nombre_completo(self, obj):
        return obj.nombre_completo


# Administración de visitas, filtros, búsqueda y acciones masivas.
@admin.register(Visita)
class VisitaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rut", "motivo_visita", "fecha", "hora_entrada", "hora_salida", "estado",
    )
    search_fields = ("persona__nombre", "persona__rut", "motivo_visita")
    list_filter = ("fecha",)
    date_hierarchy = "fecha"
    ordering = ("-fecha", "-hora_entrada")
    list_per_page = 25
    actions = (marcar_salida,)
    list_select_related = ("persona",)
    autocomplete_fields = ("persona",)

    def get_readonly_fields(self, request, obj=None):
        return ()

    # Permite buscar por RUT incluso con puntos o sin guion.
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request,
            queryset,
            search_term,
        )
        try:
            rut = normalizar_rut(search_term)
        except ValidationError:
            return queryset, use_distinct

        return (
            queryset | self.model.objects.filter(persona__rut=rut),
            use_distinct,
        )

    # Muestra visualmente si la persona continúa dentro del recinto.
    @admin.display(description="Estado", ordering="hora_salida")
    def estado(self, obj):
        return "Dentro" if obj.esta_dentro else "Salida registrada"
