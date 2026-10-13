# Dependencias y validadores usados por el formulario.
from django import forms
from .models import Persona, Visita
from .validators import normalizar_rut, validar_nombre


# Formulario público para registrar una visita y sus datos personales.
class VisitaForm(forms.ModelForm):
    # Datos de identidad visibles en el formulario de recepción.
    nombre = forms.CharField(
        label="Nombre",
        max_length=15,
        required=True,
        strip=False,
        validators=[validar_nombre],
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-xl border border-orange-200 bg-white/80 px-3 py-2.5 text-stone-950 shadow-sm outline-none transition duration-200 placeholder:text-stone-400 hover:border-orange-300 focus:border-orange-600 focus:bg-white focus:ring-4 focus:ring-orange-100',
            'placeholder': 'Ingrese su nombre',
            'autocomplete': 'off',
            'pattern': r'\S+',
            'title': 'Ingrese solo letras, sin espacios.',
        }),
    )
    apellido = forms.CharField(
        label="Apellido",
        max_length=50,
        required=True,
        strip=False,
        validators=[validar_nombre],
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-xl border border-orange-200 bg-white/80 px-3 py-2.5 text-stone-950 shadow-sm outline-none transition duration-200 placeholder:text-stone-400 hover:border-orange-300 focus:border-orange-600 focus:bg-white focus:ring-4 focus:ring-orange-100',
            'placeholder': 'Ingrese su apellido',
            'autocomplete': 'family-name',
            'pattern': r'\S+',
            'title': 'Ingrese solo letras, sin espacios.',
        }),
    )
    rut = forms.CharField(
        label='RUT',
        required=True,
        help_text='Formato: 12345678-5. Se valida automáticamente el dígito verificador.',
        widget=forms.TextInput(attrs={
            'class': 'w-full rounded-xl border border-orange-200 bg-white/80 px-3 py-2.5 text-stone-950 shadow-sm outline-none transition duration-200 placeholder:text-stone-400 hover:border-orange-300 focus:border-orange-600 focus:bg-white focus:ring-4 focus:ring-orange-100',
            'placeholder': 'Ejemplo: 12345678-5',
            'pattern': r'\d{7,8}-[\dKk]',
            'inputmode': 'text',
        }),
    )

    # Campos propios de una visita y estilos del formulario público.
    class Meta:
        model = Visita
        fields = ['nombre', 'apellido', 'rut', 'motivo_visita', 'fecha', 'hora_entrada']
        widgets = {
            'motivo_visita': forms.Textarea(attrs={
                'class': 'min-h-28 w-full resize-y rounded-xl border border-orange-200 bg-white/80 px-3 py-2.5 text-stone-950 shadow-sm outline-none transition duration-200 placeholder:text-stone-400 hover:border-orange-300 focus:border-orange-600 focus:bg-white focus:ring-4 focus:ring-orange-100',
                'placeholder': 'Describe el motivo de la visita',
                'rows': 4,
            }),
            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full rounded-xl border border-orange-200 bg-white/80 px-3 py-2.5 text-stone-950 shadow-sm outline-none transition duration-200 hover:border-orange-300 focus:border-orange-600 focus:bg-white focus:ring-4 focus:ring-orange-100',
            }),
            'hora_entrada': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full rounded-xl border border-orange-200 bg-white/80 px-3 py-2.5 text-stone-950 shadow-sm outline-none transition duration-200 hover:border-orange-300 focus:border-orange-600 focus:bg-white focus:ring-4 focus:ring-orange-100',
            }),
        }

    # Carga los datos de la persona al editar desde una interfaz autorizada.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["nombre"].initial = self.instance.persona.nombre
            self.fields["apellido"].initial = self.instance.persona.apellido
            self.fields["rut"].initial = self.instance.persona.rut

    # Valida que la entrada no ocurra antes de la fecha solicitada.
    def clean(self):
        cleaned_data = super().clean()
        if self.instance and self.instance.pk:
            return cleaned_data

        fecha = cleaned_data.get("fecha")
        hora_entrada = cleaned_data.get("hora_entrada")
        if fecha and hora_entrada and hora_entrada.date() < fecha:
            self.add_error(
                "hora_entrada",
                "La fecha de entrada no puede ser anterior a la fecha solicitada.",
            )
        return cleaned_data

    # Normaliza y valida el RUT chileno antes de guardar.
    def clean_rut(self):
        return normalizar_rut(self.cleaned_data["rut"])

    # Reutiliza la persona existente o crea una nueva relación.
    def save(self, commit=True):
        visita = super().save(commit=False)
        persona, _ = Persona.objects.get_or_create(
            rut=self.cleaned_data["rut"],
            defaults={
                "nombre": self.cleaned_data["nombre"],
                "apellido": self.cleaned_data["apellido"],
            },
        )
        if (
            persona.nombre != self.cleaned_data["nombre"]
            or persona.apellido != self.cleaned_data["apellido"]
        ):
            persona.nombre = self.cleaned_data["nombre"]
            persona.apellido = self.cleaned_data["apellido"]
            persona.save(update_fields=["nombre", "apellido"])
        visita.persona = persona
        if commit:
            visita.save()
        return visita