# Dependencias de Django y componentes de la aplicación.
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Visita
from .forms import VisitaForm

from django.views.decorators.csrf import csrf_protect


# Listado público de visitas, ordenado y dividido en páginas.
def visita_list(request):
    visitas = Visita.objects.select_related("persona").order_by(
        "-fecha",
        "-hora_entrada",
    )
    paginator = Paginator(visitas, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "visita/lista_visita.html",
        {
            "object_list": page_obj,
            "page_obj": page_obj,
            "total_visitas": paginator.count,
        },
    )


# Ficha detallada de una visita registrada.
def visita_detail(request, pk):
    visita = get_object_or_404(
        Visita.objects.select_related("persona"),
        pk=pk,
    )
    return render(request, 'visita/detalle_visita.html', {'object': visita})


# Creación pública de visitas con mensajes de éxito y error.
@csrf_protect
def visita_create(request):
    if request.method == 'POST':
        form = VisitaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "La visita se registró correctamente.",
            )
            return redirect('visita_list')
        messages.error(
            request,
            "No se pudo registrar la visita. Revisa los campos marcados.",
        )
    else:
        form = VisitaForm()
    return render(request, 'visita/formulario_visita.html', {'form': form})


# La edición pública está bloqueada; el Admin conserva esta capacidad.
@csrf_protect
def visita_update(request, pk):
    raise PermissionDenied("Las visitas no se pueden editar después de registrarse.")


# La eliminación pública está bloqueada; solo se permite desde Django Admin.
@csrf_protect
def visita_delete(request, pk):
    raise PermissionDenied(
        "Los registros solo pueden eliminarse desde el panel de administración."
    )