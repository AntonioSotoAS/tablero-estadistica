from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView, TemplateView
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.http import JsonResponse, HttpResponseBadRequest
from datetime import datetime, timedelta                                                      
from django.utils.timezone import now, localtime
from datetime import timedelta
from collections import defaultdict
from calendar import month_name
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import locale
from django.utils import timezone
import json
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from .utils import crear_snapshot_modificado
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.db import transaction
from django.db.models.functions import Coalesce, Concat
from .auditoria import marcar_audit
from django.db.models import (
    Sum, Subquery, OuterRef, Value, IntegerField, F, ExpressionWrapper,Q,CharField,FloatField, Max, Case, When
)


from .forms import ModuloForm, AsignacionJuezForm, EstProdAnualForm, JuezForm, InstanciaModuloForm, MetaConfFormSet
from bases.models import usuario
from .models import mae_est_jueces , mae_est_juez_tipos, mae_est_modulos, mae_est_escalas,\
                    mov_est_instancia_jueces, hst_usuario_accion,\
                    mov_est_instancia_usuarios, mov_est_estprod_anuales,\
                    mae_est_instancia, mae_est_meta_resumenes, mae_est_organo_jurisdiccionales, mae_est_escala_detalle,\
                    mov_est_instancia_modulos, mae_est_meta_detalles, mov_est_modulo_usuarios, \
                    conf_est_meta_conf, mae_est_meta_resumenes_modificado, \
                    aud_mae_est_meta_resumenes_modificado

#!========================================================
#!===================== JUECES ===========================
#!========================================================
class JuecesListView(View):
    def get(self, request):
        # Incluimos el tipo de juez en la consulta
        jueces = mae_est_jueces.objects.select_related('usuario', 'n_id_juez_tipo').values(
            'n_id_juez', 
            'usuario__x_dni', 
            'usuario__username',
            'usuario__x_nombres', 
            'usuario__x_app_paterno', 
            'usuario__x_app_materno', 
            'n_id_juez_tipo__x_descripcion',
            'l_activo',
            'usuario_id',
            'n_id_juez_tipo_id'
        )

        usuarios = usuario.objects.all().order_by('x_app_paterno').values('id', 'x_nombres', 'x_app_paterno', 'x_app_materno')
        tipos_juez = mae_est_juez_tipos.objects.all().values('n_id_juez_tipo', 'x_descripcion')

        return render(request, 'est/jueces_list.html', {
            'datos': jueces,
            'usuarios': usuarios,
            'tipos_juez': tipos_juez,
        })
    
class JuecesCreateView(View):
    def post(self, request):
        form = JuezForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    
class JuecesEditarView(View):
    def post(self, request, pk):
        modulo = get_object_or_404(mae_est_jueces, pk=pk)
        form = JuezForm(request.POST, instance=modulo)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

class JuecesDeleteView(View):
    def post(self, request, pk):
        modulo = get_object_or_404(mae_est_jueces, pk=pk)
        modulo.l_activo = 'N'
        modulo.save()
        return JsonResponse({'success': True})
    
class JuecesActivarView(View):
    def post(self, request, pk):
        modulo = get_object_or_404(mae_est_jueces, pk=pk)
        modulo.l_activo = 'S'
        modulo.save()
        return JsonResponse({'success': True})

#!========================================================
#!============ MOSTRAR JUEZ CON SU INSTANCIA =============
#!========================================================    
class JuecesInstanciaListView(View):
    def get(self, request):
        # Obtiene las instancias activas
        instancias = mae_est_instancia.objects.filter(l_ind_baja='N')

        # Obtiene los jueces activos con su información relacionada
        jueces = mae_est_jueces.objects.filter(l_activo='S').select_related('usuario')

        # Obtiene los datos de las asignaciones
        instancia_jueces = mov_est_instancia_jueces.objects.select_related(
            'n_instancia', 'n_id_juez', 'n_id_juez__usuario','n_id_juez__n_id_juez_tipo'
        ).filter(l_activo='S')

        return render(request, 'est/juez_instancia_list.html', {
            'datos': instancia_jueces,
            'instancias': instancias,
            'jueces': jueces,
        })
    
class JuecesInstanciaCreateView(View):
    def post(self, request, *args, **kwargs):
        form = AsignacionJuezForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Juez asignado correctamente.'})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    
class JuecesInstanciaDeleteView(View):
    def post(self, request, pk):
        instancia_juez = get_object_or_404(mov_est_instancia_jueces, pk=pk)
        instancia_juez.l_activo = 'N'
        instancia_juez.f_fecha_baja = localtime(now())
        instancia_juez.save()
        return JsonResponse({'success': True})

#!========================================================
#!===================== MODULOS ==========================
#!========================================================
# Vista para listar módulos
class ModuloListView(View):
    def get(self, request):
        modulos = mae_est_modulos.objects.all()
        return render(request, 'est/modulo_list.html', {'modulos': modulos})
    
class ModuloCreateView(View):
    def post(self, request):
        form = ModuloForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

class ModuloUpdateView(View):
    def post(self, request, pk):
        modulo = get_object_or_404(mae_est_modulos, pk=pk)
        form = ModuloForm(request.POST, instance=modulo)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})
    
class ModuloDeleteView(View):
    def post(self, request, pk):
        modulo = get_object_or_404(mae_est_modulos, pk=pk)
        modulo.l_activo = 'N'
        modulo.save()
        return JsonResponse({'success': True})
    
class ModuloActivarView(View):
    def post(self, request, pk):
        modulo = get_object_or_404(mae_est_modulos, pk=pk)
        modulo.l_activo = 'S'
        modulo.save()
        return JsonResponse({'success': True})

#!========================================================
#!================ MODULOS - INSTANCIAS ==================
#!========================================================
#todo: 01. Listar instancias asociados a un módulo
@login_required
def InstanciaModulosListar(request, modulo_id):
    modulo = get_object_or_404(mae_est_modulos, n_id_modulo=modulo_id)

    instancias_modulos = (
        mov_est_instancia_modulos.objects
        .filter(n_id_modulo=modulo)
        .select_related('n_instancia', 'n_instancia__c_org_jurisd')
        .order_by('n_instancia__c_org_jurisd__x_nom_org_jurisd', 'n_instancia__x_nom_instancia')
    )

    if request.method == "POST":
        form = InstanciaModuloForm(request.POST, modulo=modulo)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.n_id_modulo = modulo
            obj.save()

            # Respuesta AJAX
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "ok": True,
                    "row": {
                        "id": obj.pk,
                        "jurisdiccion": getattr(obj.n_instancia.c_org_jurisd, "x_nom_org_jurisd", ""),
                        "instancia": getattr(obj.n_instancia, "x_nom_instancia", ""),
                        "activo": obj.l_activo,
                        "creado": obj.f_fecha_creacion.strftime("%Y-%m-%d %H:%M"),
                    }
                })

            messages.success(request, "Instancia agregada correctamente.")
            return redirect(reverse("est:instancia_modulos_list", args=[modulo_id]))
        else:
            # Errores para AJAX
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"ok": False, "errors": form.errors}, status=400)
            # No-AJAX: seguimos al render con errores
    else:
        form = InstanciaModuloForm(modulo=modulo)

    return render(
        request,
        'est/instancia_modulos_list.html',
        {
            "modulo": modulo,
            "instancias_modulos": instancias_modulos,
            "form": form,
        }
    )

#!========================================================
#!===================== INSTANCIAS =======================
#!========================================================
class InstanciasListView(View):
    def get(self, request):
        instancias = mae_est_instancia.objects.all()
        return render(request, 'est/instancias_list.html', {'instancias': instancias})

#!========================================================
#!======================= ESCALA =======================
#!========================================================
class EscalaListView(CreateView):
    def get(self, request):
        escalas = mae_est_escalas.objects.all()
        return render(request, 'est/escala_list.html', {'escalas': escalas})

@login_required
def agregar_detalle_escala(request, escala_id):
    escala = get_object_or_404(mae_est_escalas, n_id_escala=escala_id)
    meses = {
        "1": "Enero", "2": "Febrero", "3": "Marzo", "4": "Abril", "5": "Mayo", "6": "Junio",
        "7": "Julio", "8": "Agosto", "9": "Septiembre", "10": "Octubre", "11": "Noviembre", "12": "Diciembre"
    }

    # Obtener los detalles con los nombres de los meses
    detalles = (
        mae_est_escala_detalle.objects.filter(n_id_escala=escala)
        .select_related('n_id_escala')
        .values('x_mes', 'm_porcentaje')
    )
    
    # Convertir x_mes al nombre del mes
    detalle_con_meses = [
        {'x_mes': meses.get(detalle['x_mes'], 'Desconocido'), 'm_porcentaje': detalle['m_porcentaje']}
        for detalle in detalles
    ]

    return render (request, 'est/escala_detalle_list.html', {'detalle': detalle_con_meses})

@login_required
def listar_escala(request):
    escala = mae_est_escalas.objects.all()
    return render(request, 'est/escala_list.html', {'dato': escala})

def get_escala_data(request, pk):
    escala = get_object_or_404(mae_est_escalas, pk=pk)
    data = {
        'x_nombre': escala.x_nombre,
        'update_url': reverse('est:escala_edit', args=[escala.pk]),
    }
    return JsonResponse(data)

#!========================================================
#!============ ESTANDAR DE PRODUCCIÓN ====================
#!========================================================
class ListarEstProdView(View):
    def get(self, request):
        # Obtenemos los registros activos
        estandarprod = mov_est_estprod_anuales.objects.filter(l_activo='1').select_related('n_instancia')

        # Obtenemos las instancias activas
        instancias = mae_est_instancia.objects.filter(l_ind_baja='N')  # Ajusta el filtro si es necesario
        
        # Pasamos los datos al template
        form = EstProdAnualForm()
        return render(request, "est/estandar_produc_list.html", {
            "estandarprod": estandarprod,
            "form": form,
            "instancias": instancias
        })

# Vista para guardar el formulario
class EstProdAnualCreateView(View):
    def post(self, request):
        form = EstProdAnualForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors})

#!========================================================
#!============ CONFIGURACION DE METASS ===================
#!========================================================
class ConfiguracionMetas(LoginRequiredMixin, ListView):
    model = conf_est_meta_conf
    template_name = 'est/configuracion_metas.html'
    context_object_name = 'obj'

    def _get_periodo(self):
        today = timezone.localdate()
        try:
            year = int(self.request.GET.get('year', today.year))
        except (TypeError, ValueError):
            year = today.year
        try:
            month = int(self.request.GET.get('month', today.month))
        except (TypeError, ValueError):
            month = today.month
        # Sanitiza el mes (1..12)
        if month < 1 or month > 12:
            month = today.month
        return year, month

    def get_queryset(self):
        year, month = self._get_periodo()
        return (
            conf_est_meta_conf.objects
            .filter(n_anio_est=year, n_mes_est=month)
            .select_related('n_instancia', 'usuario')
            .order_by('n_instancia__c_org_jurisd__x_nom_org_jurisd',
                      'n_instancia__x_nom_instancia')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        year, month = self._get_periodo()
        meses = ["", "enero","febrero","marzo","abril","mayo","junio",
                 "julio","agosto","septiembre","octubre","noviembre","diciembre"]

        # Total de "instancias fuente" = instancias presentes en factores (distintas)
        inst_total = (
            mov_est_estprod_anuales.objects
            .filter(l_activo='S')  # si corresponde
            .values('n_instancia_id').distinct().count()
        )

        # Ya configuradas en conf_est_meta_conf para ese periodo (entre las de factores)
        existentes_distintos = (
            conf_est_meta_conf.objects
            .filter(n_anio_est=year, n_mes_est=month,
                    n_instancia_id__in=mov_est_estprod_anuales.objects
                        .filter(l_activo='S')
                        .values_list('n_instancia_id', flat=True).distinct())
            .values('n_instancia_id').distinct().count()
        )

        faltantes = max(inst_total - existentes_distintos, 0)

        seed_url = f"{reverse('est:meta_conf_seed')}?year={year}&month={month}"

        ctx.update({
            "year": year,
            "month": month,
            "month_name": meses[month],
            "inst_total": inst_total,
            "existentes": existentes_distintos,
            "faltantes": faltantes,
            "seed_url": seed_url,
        })
        return ctx

@login_required
def meta_conf_seed_view(request):
    today = timezone.localdate()
    try:
        year = int(request.GET.get('year', today.year))
    except (TypeError, ValueError):
        year = today.year
    try:
        month = int(request.GET.get('month', today.month))
    except (TypeError, ValueError):
        month = today.month
    if month < 1 or month > 12:
        month = today.month

    # IDs de instancias provenientes de factores (únicos)
    todas_inst_ids = list(
        mov_est_estprod_anuales.objects
        .filter(l_activo='S')
        .values_list('n_instancia_id', flat=True)
        .distinct()
    )

    # Ya existentes para el periodo (entre esas instancias)
    existentes_set = set(
        conf_est_meta_conf.objects
        .filter(n_anio_est=year, n_mes_est=month,
                n_instancia_id__in=todas_inst_ids)
        .values_list('n_instancia_id', flat=True)
    )

    faltantes_ids = [i for i in todas_inst_ids if i not in existentes_set]

    if request.method == "POST":
        nuevos = [
            conf_est_meta_conf(
                n_instancia_id=inst_id,
                usuario=None,                 # vacío
                n_anio_est=year,
                n_mes_est=month,
                m_op_egre_otra_dep=0,
                m_op_ing_otra_dep=0,
                m_op_pend_reserva=0,
                f_fecha_mod=None,            # vacío
            )
            for inst_id in faltantes_ids
        ]

        with transaction.atomic():
            if nuevos:
                # Si agregas UniqueConstraint (instancia, anio, mes), puedes usar ignore_conflicts=True
                conf_est_meta_conf.objects.bulk_create(nuevos, batch_size=1000)

        messages.success(
            request,
            f"Periodo {year}-{month:02d}: creados {len(nuevos)} registros. Ya existían {len(existentes_set)}."
        )
        return redirect(f"{reverse('est:configuracion_metas_list')}?year={year}&month={month}")

    # GET: solo informa y vuelve al listado
    messages.info(
        request,
        f"Periodo {year}-{month:02d}: existen {len(existentes_set)}; faltan {len(faltantes_ids)}. "
        f"Presiona 'Completar faltantes' para crearlos."
    )
    return redirect(f"{reverse('est:configuracion_metas_list')}?year={year}&month={month}")

#? ===========================================================================================
#? ========================= TABLERO DE CONTROL DE PRESIDENCIA ===============================
#? ===========================================================================================
#!========================================================
#!================== ESTADISTICA =========================
#!========================================================   
@login_required
def Estadistica(request):
    accion = 'Consulta Menú Estadistico'

    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )
    return render(request,"est/estadistica_menu.html")

#* El usuario con sesión activa podrá visualizar los módulos al que fue asignado
#* el permiso que tiene es ---- perm.mov.est_modulo_usuarios
@login_required
def Estadistica_por_modulo(request):
    # Obtener el usuario activo (autenticado)
    usuario_actual = request.user
    
    # Obtener los módulos asignados al usuario activo
    modulos_asignados = mae_est_modulos.objects.filter(
        mov_est_modulo_usuarios__usuario=usuario_actual,  # Relación con la tabla de movimientos
        l_activo='S'  # Solo módulos activos
    ).distinct()  # Evitar duplicados en caso de relaciones múltiples

    accion = 'Consulta Estadistica por Módulo'
    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )

    # Renderizar la plantilla con los módulos asignados
    return render(request, "est/estadistica_modulos.html", {'dato': modulos_asignados})

@login_required
def Estadistica_descripcion(request, modulo_id):
    usuario_actual = request.user

    modulos_asignados = mae_est_modulos.objects.filter(
        n_id_modulo=modulo_id,
        mov_est_modulo_usuarios__usuario=usuario_actual,
        l_activo='S'
    ).distinct()
    if not modulos_asignados.exists():
        raise Http404("Módulo no encontrado o sin acceso.")
    modulo = modulos_asignados.first()

    # Instancias del módulo (vínculo activo)
    instancias_ids = (mae_est_instancia.objects
        .filter(
            mov_est_instancia_modulos__n_id_modulo=modulo,
            mov_est_instancia_modulos__l_activo='S'
        )
        .values_list('pk', flat=True)
        .distinct()
    )

    # TODOS los jueces activos por instancia (no solo el más reciente)
    jueces_modulo = (
        mov_est_instancia_jueces.objects
        .filter(n_instancia_id__in=instancias_ids, l_activo='S')
        .select_related('n_instancia', 'n_instancia__c_org_jurisd', 'n_id_juez__usuario')
        .annotate(
            juez_fullname=Concat(
                'n_id_juez__usuario__x_nombres', Value(' '),
                'n_id_juez__usuario__x_app_paterno', Value(' '),
                'n_id_juez__usuario__x_app_materno',
                output_field=CharField()
            ),
            org_jurisd=F('n_instancia__c_org_jurisd__x_nom_org_jurisd'),
            instancia_nombre=F('n_instancia__x_nom_instancia'),
            instancia_corto=F('n_instancia__x_corto'),
        )
        .order_by('org_jurisd', 'instancia_nombre', '-f_fecha_creacion')
    )

    # Log
    accion = f'Ingreso a Detalle del Módulo {modulo.n_id_modulo}'
    existe = hst_usuario_accion.objects.filter(
        usuario=usuario_actual, x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()
    if not existe:
        hst_usuario_accion.objects.create(usuario=usuario_actual, x_accion=accion)

    return render(
        request,
        "est/estadistica_desc_modulos.html",
        {"modulo": modulo, "jueces_modulo": jueces_modulo}
    )

#!========================================================
#!====== ESTADISTICA POR MODULO MOSTRANDO GRAFICO ========
#!========================================================   
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
import locale

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, OuterRef, Subquery, Value, CharField, F
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now

# Asumo que ya importaste tus modelos:
# from .models import (mae_est_modulos, mae_est_instancia, mae_est_meta_resumenes,
#                      mae_est_escala_detalle, mov_est_instancia_jueces, hst_usuario_accion)

@login_required
def Estadistica_modulo_grafica(request, modulo_id):
    # Locale español (si no está disponible en el OS, se ignora el error)
    try:
        locale.setlocale(locale.LC_ALL, 'es_PE.UTF-8')
    except locale.Error as e:
        print(f"Error al configurar el locale: {e}")

    modulo = get_object_or_404(mae_est_modulos, pk=modulo_id)

    today = datetime.now()
    year = today.year
    actual_month = today.month
    prev_month = actual_month - 1 if actual_month > 1 else 12
    prev_year = year if actual_month > 1 else year - 1

    # Helpers x_mes tolerante a "9" y "09"
    x_mes_actual_opts = {str(actual_month), f"{actual_month:02d}"}
    x_mes_prev_opts   = {str(prev_month),   f"{prev_month:02d}"}

    # === Escalas: Meta Ideal ===
    # Si usas varias escalas y necesitas filtrar por n_id_escala, ajusta aquí.
    meta_ideal_A = (mae_est_escala_detalle.objects
                    .filter(x_mes__in=x_mes_actual_opts)
                    .order_by('-n_id_escala_detalle')
                    .values_list('m_porcentaje', flat=True)
                    .first())
    meta_ideal_C = (mae_est_escala_detalle.objects
                    .filter(x_mes__in=x_mes_prev_opts)
                    .order_by('-n_id_escala_detalle')
                    .values_list('m_porcentaje', flat=True)
                    .first())

    # Default en caso no haya registro en la escala
    meta_ideal_A = float(meta_ideal_A) if meta_ideal_A is not None else 0.0
    meta_ideal_C = float(meta_ideal_C) if meta_ideal_C is not None else 0.0

    # Subquery para nombre completo del juez activo más reciente
    juez_fullname_subquery = (mov_est_instancia_jueces.objects
        .filter(n_instancia=OuterRef('n_instancia__pk'), l_activo='S')
        .order_by('-f_fecha_creacion')
        .annotate(fullname=Concat(
            'n_id_juez__usuario__x_nombres', Value(' '),
            'n_id_juez__usuario__x_app_paterno', Value(' '),
            'n_id_juez__usuario__x_app_materno',
            output_field=CharField()
        ))
        .values('fullname')[:1]
    )

    # === Mes Actual (estado = A) ===
    resumenes_actual_qs = (mae_est_meta_resumenes.objects
        .filter(
            n_id_modulo=modulo,
            n_anio_est=year,
            n_mes_est=actual_month,
            l_estado='A'
        )
        .values(
            'n_instancia__x_corto',
            'n_instancia__x_nom_instancia',
            'n_instancia__c_org_jurisd__x_nom_org_jurisd',
            'f_fecha_mod',
            'x_situacion_carga',
            'x_niv_produc',
            'm_avan_meta',
            'm_ideal_avan_meta',
            'm_meta_preliminar',
            'n_carg_procesal_ini',
        )
        .annotate(
            total_ingreso=Sum('m_t_ingreso'),
            total_resuelto=Sum('m_t_resuelto'),
            juez_nombre=Subquery(juez_fullname_subquery)
        )
        .order_by('n_instancia__c_org_jurisd', '-m_avan_meta')
    )

    # Meses en español (sin depender de locale del SO)
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    fecha_actual = f"{today.day} de {meses[today.month]} de {today.year}"

    # Fecha de modificación de referencia (opcional)
    try:
        fecha_modificacion = mae_est_meta_resumenes.objects.get(n_id_meta_resumen=1).f_fecha_mod
        fecha_modificacion_formateada = (
            f"{fecha_modificacion.day} de {meses[fecha_modificacion.month]} de {fecha_modificacion.year} "
            f"a las {fecha_modificacion.strftime('%H:%M')} hrs."
        )
    except mae_est_meta_resumenes.DoesNotExist:
        fecha_modificacion_formateada = "Sin fecha"

    # Agrupar por órgano jurisdiccional y preparar arreglo plano `instancias`
    agrupados = defaultdict(list)
    instancias_list = []

    for resumen in resumenes_actual_qs:
        r = dict(resumen)
        r['estado'] = 'A'
        r['m_avan_meta'] = float(r['m_avan_meta'] or 0)
        r['m_ideal_avan_meta'] = float(r['m_ideal_avan_meta'] or 0)
        r['f_fecha_mod'] = r['f_fecha_mod'].strftime('%d/%m/%Y a las %H:%M') if r['f_fecha_mod'] else 'Sin fecha'
        r['juez_nombre'] = r.get('juez_nombre') or 'Sin juez asignado'
        agrupados[r['n_instancia__c_org_jurisd__x_nom_org_jurisd']].append(r)
        instancias_list.append(r)

    # (Opcional) Datos para otros gráficos que ya generabas
    chart_data = []
    unique_instancias = set()
    for org_jurisd, resumenes in agrupados.items():
        org_data = {'org_jurisd': org_jurisd, 'instancias': {}}
        for r in resumenes:
            inst = r['n_instancia__x_corto']
            unique_instancias.add(inst)
            org_data['instancias'][inst] = r['m_avan_meta']
        chart_data.append(org_data)

    context = {
        "modulo": modulo,
        "agrupados": dict(agrupados),
        "instancias": instancias_list,          # <-- para tu script ECharts
        "meta_ideal_A": meta_ideal_A,           # <-- markLine Mes Actual
        "meta_ideal_C": meta_ideal_C,           # <-- markLine Mes Cerrado (mes previo)
        "mes_actual": meses[actual_month],
        "anio_actual": year,
        "fecha_actual": fecha_actual,
        "fecha_modificacion": fecha_modificacion_formateada,
        "chart_data": chart_data,
        "unique_instancias": list(unique_instancias),
    }

    # Log de acción (antiflood 10s)
    accion = 'Consulta Gráfico Estadistico'
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()
    if not existe:
        hst_usuario_accion.objects.create(usuario=request.user, x_accion=accion)

    return render(request, 'est/estadistica_modulos_grafica.html', context)

@login_required
def Estadistica_actual_cerrado(request, modulo_id):
    # Locale español (si no está disponible en el OS, se ignora el error)
    try:
        locale.setlocale(locale.LC_ALL, 'es_PE.UTF-8')
    except locale.Error as e:
        print(f"Error al configurar el locale: {e}")

    modulo = get_object_or_404(mae_est_modulos, pk=modulo_id)

    today = datetime.now()
    year = today.year
    actual_month = today.month
    prev_month = actual_month - 1 if actual_month > 1 else 12
    prev_year = year if actual_month > 1 else year - 1

    # Helpers x_mes tolerante a "9" y "09"
    x_mes_actual_opts = {str(actual_month), f"{actual_month:02d}"}
    x_mes_prev_opts   = {str(prev_month),   f"{prev_month:02d}"}

    # === Escalas: Meta Ideal ===
    # Si usas varias escalas y necesitas filtrar por n_id_escala, ajusta aquí.
    meta_ideal_A = (mae_est_escala_detalle.objects
                    .filter(x_mes__in=x_mes_actual_opts)
                    .order_by('-n_id_escala_detalle')
                    .values_list('m_porcentaje', flat=True)
                    .first())
    meta_ideal_C = (mae_est_escala_detalle.objects
                    .filter(x_mes__in=x_mes_prev_opts)
                    .order_by('-n_id_escala_detalle')
                    .values_list('m_porcentaje', flat=True)
                    .first())

    # Default en caso no haya registro en la escala
    meta_ideal_A = float(meta_ideal_A) if meta_ideal_A is not None else 0.0
    meta_ideal_C = float(meta_ideal_C) if meta_ideal_C is not None else 0.0

    # Subquery para nombre completo del juez activo más reciente
    juez_fullname_subquery = (mov_est_instancia_jueces.objects
        .filter(n_instancia=OuterRef('n_instancia__pk'), l_activo='S')
        .order_by('-f_fecha_creacion')
        .annotate(fullname=Concat(
            'n_id_juez__usuario__x_nombres', Value(' '),
            'n_id_juez__usuario__x_app_paterno', Value(' '),
            'n_id_juez__usuario__x_app_materno',
            output_field=CharField()
        ))
        .values('fullname')[:1]
    )

    # === Mes Actual (estado = A) ===
    resumenes_actual_qs = (mae_est_meta_resumenes.objects
        .filter(
            n_id_modulo=modulo,
            n_anio_est=year,
            n_mes_est=actual_month,
            l_estado='A'
        )
        .values(
            'n_instancia__x_corto',
            'n_instancia__x_nom_instancia',
            'n_instancia__c_org_jurisd__x_nom_org_jurisd',
            'f_fecha_mod',
            'x_situacion_carga',
            'x_niv_produc',
            'm_avan_meta',
            'm_ideal_avan_meta',
            'm_meta_preliminar',
            'n_carg_procesal_ini',
        )
        .annotate(
            total_ingreso=Sum('m_t_ingreso'),
            total_resuelto=Sum('m_t_resuelto'),
            juez_nombre=Subquery(juez_fullname_subquery)
        )
        .order_by('n_instancia__c_org_jurisd', '-m_avan_meta')
    )

    # === Mes Cerrado (estado = C) del mes anterior ===
    resumenes_cerrado_qs = (mae_est_meta_resumenes.objects
        .filter(
            n_id_modulo=modulo,
            n_anio_est=prev_year,
            n_mes_est=prev_month,
            l_estado='C'
        )
        .values(
            'n_instancia__x_corto',
            'n_instancia__x_nom_instancia',
            'n_instancia__c_org_jurisd__x_nom_org_jurisd',
            'f_fecha_mod',
            'x_situacion_carga',
            'x_niv_produc',
            'm_avan_meta',
            'm_ideal_avan_meta',
            'm_meta_preliminar',
            'n_carg_procesal_ini',
        )
        .annotate(
            total_ingreso=Sum('m_t_ingreso'),
            total_resuelto=Sum('m_t_resuelto'),
            juez_nombre=Subquery(juez_fullname_subquery)
        )
        .order_by('n_instancia__c_org_jurisd', '-m_avan_meta')
    )

    # Meses en español (sin depender de locale del SO)
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    fecha_actual = f"{today.day} de {meses[today.month]} de {today.year}"

    # Fecha de modificación de referencia (opcional)
    try:
        fecha_modificacion = mae_est_meta_resumenes.objects.get(n_id_meta_resumen=1).f_fecha_mod
        fecha_modificacion_formateada = (
            f"{fecha_modificacion.day} de {meses[fecha_modificacion.month]} de {fecha_modificacion.year} "
            f"a las {fecha_modificacion.strftime('%H:%M')} hrs."
        )
    except mae_est_meta_resumenes.DoesNotExist:
        fecha_modificacion_formateada = "Sin fecha"

    # Agrupar por órgano jurisdiccional y preparar arreglo plano `instancias`
    agrupados = defaultdict(list)
    instancias_list = []

    for resumen in resumenes_actual_qs:
        r = dict(resumen)
        r['estado'] = 'A'
        r['m_avan_meta'] = float(r['m_avan_meta'] or 0)
        r['m_ideal_avan_meta'] = float(r['m_ideal_avan_meta'] or 0)
        r['f_fecha_mod'] = r['f_fecha_mod'].strftime('%d/%m/%Y a las %H:%M') if r['f_fecha_mod'] else 'Sin fecha'
        r['juez_nombre'] = r.get('juez_nombre') or 'Sin juez asignado'
        agrupados[r['n_instancia__c_org_jurisd__x_nom_org_jurisd']].append(r)
        instancias_list.append(r)

    for resumen in resumenes_cerrado_qs:
        r = dict(resumen)
        r['estado'] = 'C'
        r['m_avan_meta'] = float(r['m_avan_meta'] or 0)
        r['m_ideal_avan_meta'] = float(r['m_ideal_avan_meta'] or 0)
        r['f_fecha_mod'] = r['f_fecha_mod'].strftime('%d/%m/%Y a las %H:%M') if r['f_fecha_mod'] else 'Sin fecha'
        r['juez_nombre'] = r.get('juez_nombre') or 'Sin juez asignado'
        agrupados[r['n_instancia__c_org_jurisd__x_nom_org_jurisd']].append(r)
        instancias_list.append(r)

    # (Opcional) Datos para otros gráficos que ya generabas
    chart_data = []
    unique_instancias = set()
    for org_jurisd, resumenes in agrupados.items():
        org_data = {'org_jurisd': org_jurisd, 'instancias': {}}
        for r in resumenes:
            inst = r['n_instancia__x_corto']
            unique_instancias.add(inst)
            org_data['instancias'][inst] = r['m_avan_meta']
        chart_data.append(org_data)

    context = {
        "modulo": modulo,
        "agrupados": dict(agrupados),
        "instancias": instancias_list,          # <-- para tu script ECharts
        "meta_ideal_A": meta_ideal_A,           # <-- markLine Mes Actual
        "meta_ideal_C": meta_ideal_C,           # <-- markLine Mes Cerrado (mes previo)
        "mes_actual": meses[actual_month],
        "anio_actual": year,
        "fecha_actual": fecha_actual,
        "fecha_modificacion": fecha_modificacion_formateada,
        "chart_data": chart_data,
        "unique_instancias": list(unique_instancias),
    }

    # Log de acción (antiflood 10s)
    accion = 'Consulta Gráfico Estadistico'
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()
    if not existe:
        hst_usuario_accion.objects.create(usuario=request.user, x_accion=accion)

    return render(request, 'est/estadistica_actual_cerrado.html', context)

#!========================================================
#!====== ESTADISTICA MENSUAL ========
#!========================================================   
@login_required
def Estadistica_mensual(request, modulo_id):
    try:
        locale.setlocale(locale.LC_ALL, 'es_PE.UTF-8')
    except locale.Error as e:
        print(f"Error al configurar el locale: {e}")

    modulo = get_object_or_404(mae_est_modulos, pk=modulo_id)

    today = now()
    year = today.year
    actual_month = today.month

    juez_fullname_subquery = mov_est_instancia_jueces.objects.filter(
        n_instancia=OuterRef('n_instancia__pk'),
        l_activo='S'
    ).order_by('-f_fecha_creacion').annotate(
        fullname=Concat(
            'n_id_juez__usuario__x_nombres', Value(' '),
            'n_id_juez__usuario__x_app_paterno', Value(' '),
            'n_id_juez__usuario__x_app_materno',
            output_field=CharField()
        )
    ).values('fullname')[:1]

    resumenes_por_mes = mae_est_meta_resumenes.objects.filter(
        n_id_modulo=modulo,
        n_anio_est=year
    ).values(
        'n_mes_est',
        'n_instancia__x_corto',
        'n_instancia__x_nom_instancia',
        'n_instancia__c_org_jurisd__x_nom_org_jurisd',
        'm_avan_meta',
        'm_ideal_avan_meta',
        'f_fecha_mod'
    ).annotate(
        juez_nombre=Subquery(juez_fullname_subquery)
    ).order_by('n_mes_est', 'n_instancia__c_org_jurisd', '-m_avan_meta')

    # Agrupar por mes
    agrupado_por_mes = defaultdict(list)
    agrupados = defaultdict(list)
    for resumen in resumenes_por_mes:
        # Normalización
        resumen['m_avan_meta'] = float(resumen['m_avan_meta'] or 0)
        resumen['m_ideal_avan_meta'] = float(resumen['m_ideal_avan_meta'] or 0)
        resumen['f_fecha_mod'] = resumen['f_fecha_mod'].strftime('%d/%m/%Y') if resumen['f_fecha_mod'] else 'Sin fecha'
        resumen['juez_nombre'] = resumen.get('juez_nombre') or 'Sin juez asignado'

        # Agrupar por mes
        mes = resumen['n_mes_est']
        agrupado_por_mes[mes].append(resumen)

        # Agrupar por jurisdicción
        jurisdiccion = resumen['n_instancia__c_org_jurisd__x_nom_org_jurisd']
        agrupados[jurisdiccion].append(resumen)

    # Opcional: obtener fecha de modificación para mostrar en encabezado
    try:
        fecha_modificacion = mae_est_meta_resumenes.objects.get(n_id_meta_resumen=1).f_fecha_mod
        meses = {
            1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
            5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
            9: "SETIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
        }
        fecha_actual = f"{today.day} de {meses[today.month]} de {today.year}"
        fecha_modificacion_formateada = (
            f"{fecha_modificacion.day} de {meses[fecha_modificacion.month]} de {fecha_modificacion.year} a las {fecha_modificacion.strftime('%H:%M')} hrs."
        )
    except mae_est_meta_resumenes.DoesNotExist:
        fecha_modificacion_formateada = "Sin fecha"
        fecha_actual = ""

    context = {
        "modulo": modulo,
        "datos_por_mes": dict(agrupado_por_mes),
        "agrupados": dict(agrupados),  # <-- necesario para {% for jurisdiccion, instancias in agrupados.items %}
        "meses_nombre": {
            1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL",
            5: "MAYO", 6: "JUNIO", 7: "JULIO", 8: "AGOSTO",
            9: "SETIEMBRE", 10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
        },
        "fecha_modificacion": fecha_modificacion_formateada,
        "fecha_actual": fecha_actual,
    }

    return render(request, 'est/estadistica_mensual.html', context)

#! =======================================================
#! ================= CONSULTAR POR ORGANO ================
#! ======================================================= 
@login_required
def Estadistica_por_organo(request):
    # Obtener el usuario activo (autenticado)
    usuario_actual = request.user

    # Filtrar los módulos asignados al usuario
    modulos_asignados = mov_est_modulo_usuarios.objects.filter(usuario=usuario_actual).values_list('n_id_modulo', flat=True)

    # Filtrar las instancias relacionadas con los módulos asignados
    instancias = mae_est_instancia.objects.filter(
        mov_est_instancia_modulos__n_id_modulo__in=modulos_asignados,  # Relación con los módulos
        mov_est_instancia_modulos__l_activo='S',  # Solo instancias activas en los módulos
        l_ind_baja='N'  # Solo instancias no dadas de baja
    ).distinct()  # Evitar duplicados en caso de múltiples relaciones

    # Contexto para la plantilla
    context = {
        "instancias": instancias,
    }

    accion = 'Consulta Estadistica por Organo Jurisdiccional'
    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )

    # Renderizar la plantilla con las instancias filtradas
    return render(request, 'est/estadistica_organo.html', context)

@login_required
def obtener_datos_instancia(request):
    if request.method == "GET" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        instancia_id = request.GET.get("instancia_id")
        
        # Obtener la fecha del día anterior
        yesterday = datetime.now() - timedelta(days=1)
        mes_anterior = yesterday.month
        anio_anterior = yesterday.year

        # Filtrar los datos de mae_est_meta_resumenes para la instancia seleccionada, mes y año actuales
        instancia = get_object_or_404(mae_est_instancia, pk=instancia_id)
        # Filtrar los datos usando el mes y año del día anterior
        datos = mae_est_meta_resumenes.objects.filter(
            n_instancia=instancia,
            n_mes_est=mes_anterior,
            n_anio_est=anio_anterior
        ).values(
            'n_instancia__x_nom_instancia',
            'x_situacion_carga',
            'x_niv_produc',
            'm_avan_meta',
            'm_estandar_prod',
            'm_ideal_avan_meta',
            'm_meta_preliminar',
            'n_carg_procesal_ini',
            'm_t_ingreso',
            'm_t_resuelto',
            'm_niv_bueno',
            'm_niv_muy_bueno',
            'f_fecha_mod',
        )

        # Convertir los datos a una lista y calcular el IER
        datos_lista = list(datos)
        for dato in datos_lista:
            m_t_ingreso = dato['m_t_ingreso'] or 0  # Evitar división por cero
            m_t_resuelto = dato['m_t_resuelto'] or 0
            dato['IER'] = round((m_t_resuelto / m_t_ingreso * 100) if m_t_ingreso > 0 else 0, 2)
            dato['f_fecha_mod'] = dato['f_fecha_mod'].strftime(f"%d de {month_name[dato['f_fecha_mod'].month]} de %Y") \
            if dato['f_fecha_mod'] else 'Sin fecha'


        # Retornar los datos como JSON
        return JsonResponse({"datos": list(datos)}, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

#! =======================================================
#! ======= COMPARAR INSTANCIAS COMO SI FUESE UN VS =======
#! ======================================================= 
@login_required
def comparar_instancias(request):
    organos = mae_est_organo_jurisdiccionales.objects.filter(l_activo='S')
    resumen1 = resumen2 = None
    instancia_1 = instancia_2 = None

    if request.method == 'POST':
        instancia_1_id = request.POST.get('instancia_1')
        instancia_2_id = request.POST.get('instancia_2')

        instancia_1 = mae_est_instancia.objects.get(n_instancia_id=instancia_1_id)
        instancia_2 = mae_est_instancia.objects.get(n_instancia_id=instancia_2_id)

        resumen1 = mae_est_meta_resumenes.objects.filter(n_instancia=instancia_1).last()
        resumen2 = mae_est_meta_resumenes.objects.filter(n_instancia=instancia_2).last()

    accion = 'Compara Estadistica por Juzgados'

    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )

    return render(request, 'est/estadistica_comparar.html', {
        'organos': organos,
        'resumen1': resumen1,
        'resumen2': resumen2,
        'instancia_1': instancia_1,
        'instancia_2': instancia_2,
    })

@login_required
def get_instancias_por_organo(request):
    org_id = request.GET.get('org_id')
    instancias = mae_est_instancia.objects.filter(c_org_jurisd__c_org_jurisd=org_id, l_ind_baja='N')
    data = [{'id': i.n_instancia_id, 'nombre': i.x_nom_instancia} for i in instancias]
    return JsonResponse(data, safe=False)

#! =======================================================
#! =========== VISTA DE JUEZ =================
#! ======================================================= 
@login_required
def NivelProductividad(request):
    template_name = "est/nivel_productividad.html"
    user = request.user  # Obtener el usuario actual
    context = {}

    # Verificar si el usuario está asociado a un juez activo
    juez = mae_est_jueces.objects.filter(usuario=user, l_activo='S').first()
    
    if juez:
        # Obtener las instancias asignadas al juez
        instancias_asignadas = mov_est_instancia_jueces.objects.filter(
            n_id_juez=juez, l_activo='S'
        ).select_related('n_instancia')

        # Obtener el resumen por instancia y mes
        resumen_por_instancia = {}
        for instancia in instancias_asignadas:
            resumen_por_instancia[instancia.n_instancia.x_nom_instancia] = {
                'ingresos': [0] * 12,  # Inicializamos una lista con 12 ceros para los ingresos por mes
                'resueltos': [0] * 12   # Inicializamos una lista con 12 ceros para los resueltos por mes
            }
            
            anio_actual = datetime.now().year
            # Obtener los totales de ingresos y resueltos por mes para cada instancia
            resumen_por_mes = (
                    mae_est_meta_detalles.objects.filter(
                        n_instancia=instancia.n_instancia,
                        n_anio_est=anio_actual  # Filtra solo el año presente
                    )
                .values('n_mes_est')
                .annotate(
                    total_resuelto=Sum('m_t_resuelto_mes'),
                    total_ingreso=Sum('m_t_ingreso_mes')
                )
                .order_by('n_mes_est')
            )
            
            # Llenar los totales por mes en el diccionario
            for dato in resumen_por_mes:
                mes_index = dato['n_mes_est'] - 1  # Ajuste porque los meses empiezan desde 1, pero las listas desde 0
                resumen_por_instancia[instancia.n_instancia.x_nom_instancia]['ingresos'][mes_index] = dato['total_ingreso'] or 0
                resumen_por_instancia[instancia.n_instancia.x_nom_instancia]['resueltos'][mes_index] = dato['total_resuelto'] or 0

        context['resumen_por_instancia'] = resumen_por_instancia

        # Obtener el día anterior
        fecha_actual = now()
        fecha_ayer = fecha_actual - timedelta(days=1)

        # Filtrar los datos de mae_est_meta_resumenes
        resumenes = mae_est_meta_resumenes.objects.filter(
            n_instancia__in=[instancia.n_instancia for instancia in instancias_asignadas],
            n_anio_est=fecha_ayer.year,
            n_mes_est=fecha_ayer.month
        ).select_related('n_instancia')

        resumenes_lista = []
        for resumen in resumenes:
            nombre_instancia = resumen.n_instancia.x_nom_instancia
            resumenes_lista.append({
                'id': resumen.n_id_meta_resumen,
                'instancia': nombre_instancia,
                'anio': resumen.n_anio_est,
                'mes': resumen.n_mes_est,
                'produccion': float(resumen.m_estandar_prod or 0),
                'ideal_meta': float(resumen.m_ideal_avan_meta or 0),
                'avance_meta': float(resumen.m_avan_meta or 0),
                'meta_preliminar': float(resumen.m_meta_preliminar or 0),
                'carga_inicial': int(resumen.n_carg_procesal_ini or 0),
                'situacion_carga': resumen.x_situacion_carga,
                'nivel_produc': resumen.x_niv_produc,
                'ingresos': float(resumen.m_t_ingreso or 0),
                'resueltos': float(resumen.m_t_resuelto or 0),
                'IER': round(
                    (float(resumen.m_t_resuelto) / float(resumen.m_t_ingreso)) * 100, 2
                ) if resumen.m_t_ingreso and resumen.m_t_ingreso > 0 else 0,
                'series_line': {
                    'ingresos': [float(x) for x in resumen_por_instancia.get(nombre_instancia, {}).get('ingresos', [0]*12)],
                    'resueltos': [float(x) for x in resumen_por_instancia.get(nombre_instancia, {}).get('resueltos', [0]*12)]
                }
            })

        context['resumenes'] = resumenes_lista
        context['resumenes_json'] = mark_safe(json.dumps(resumenes_lista))  # Para usar en JS
    else:
        context['resumen_por_instancia'] = {}
        context['resumenes'] = []
        context['resumenes_json'] = mark_safe(json.dumps([]))
    context['fecha_hora_actual'] = now()

    # Recuperar y formatear la fecha de modificación de mae_est_meta_resumenes
    try:
        meta_resumen = mae_est_meta_resumenes.objects.get(n_id_meta_resumen=1)  # Cambia el ID si es necesario
        f_fecha_mod = meta_resumen.f_fecha_mod
        if f_fecha_mod:
            meses = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            f_fecha_mod = f"{f_fecha_mod.day} de {meses[f_fecha_mod.month]} de {f_fecha_mod.year} a las {f_fecha_mod.strftime('%H:%M')} hrs."
        else:
            f_fecha_mod = "Fecha no disponible"
    except mae_est_meta_resumenes.DoesNotExist:
        f_fecha_mod = "Fecha no disponible"

    context['f_fecha_mod'] = f_fecha_mod

    accion = 'Verifica su Nivel de Productividad'

    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )

    # Renderizar el template con el contexto
    return render(request, template_name, context)

#! =======================================================
#! ==================== POWER BI =========================
#! ======================================================= 
@login_required
def PowerSinoe(request):
    accion = 'Visualizo Dashboard de Sinoe'

    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )
    return render(request,"est/powerbi_sinoe.html")  

@login_required
def PowerJornada(request):
    accion = 'Visualizo Dashboard de Jornadas Extraordinarias'

    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )
    return render(request,"est/powerbi_jornada.html")  

@login_required
def PowerEstadistica(request):
    accion = 'Visualizo Dashboard de Estadistica'

    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )

    return render(request,"est/powerbi_estadistica.html")  

@login_required
def PowerNepena(request):
    accion = 'Visualizo Dashboard de Nepeña'

    # Buscar si ya existe una acción igual para este usuario en los últimos 10 segundos
    existe = hst_usuario_accion.objects.filter(
        usuario=request.user,
        x_accion=accion,
        f_fecha_creacion__gte=now() - timedelta(seconds=10)
    ).exists()

    # Si no existe, crearla
    if not existe:
        hst_usuario_accion.objects.create(
            usuario=request.user,
            x_accion=accion
        )

    return render(request,"est/powerbi_nepena.html")

#? =========================================================
#? ====================== LOGISTICA ========================
#? =========================================================
@login_required
def Logistica_menu(request):
    return render(request,"est/logistica_menu.html")

@login_required
def Presupuesto_menu(request):
    return render(request,"est/presupuesto_menu.html")

@login_required
def Depositos_menu(request):
    return render(request,"est/deposito_menu.html")

@login_required
def Camaras_menu(request):
    return render(request,"est/camaras_menu.html")

#! ==============================================================
#! =============== CONFIGURACION DE METAS =======================
#! Donde la oficina de estadistica realizará modificaciones
#! en esta primera vista podrá visualizar la Meta del año actual
#! ==============================================================
class MetaResumenListView(LoginRequiredMixin, ListView):
    model = mae_est_meta_resumenes
    template_name = "est/metas_resumen_list.html"
    context_object_name = "items"

    def get_queryset(self):
        today = timezone.localdate()
        year = today.year
        month = today.month

        # (Si aún necesitas esta suma desde 'detalles' para febrero)
        subq_febrero_detalles = (
            mae_est_meta_detalles.objects
            .filter(n_anio_est=year, n_mes_est=2, n_instancia=OuterRef("n_instancia"))
            .values("n_instancia")
            .annotate(total=Sum("m_t_ingreso_mes"))
            .values("total")[:1]
        )

        subq_conf_egre = (
            conf_est_meta_conf.objects
            .filter(n_anio_est=year, n_mes_est=month, n_instancia=OuterRef("n_instancia"))
            .values("m_op_egre_otra_dep")[:1]
        )

        subq_conf_ing = (
            conf_est_meta_conf.objects
            .filter(n_anio_est=year, n_mes_est=month, n_instancia=OuterRef("n_instancia"))
            .values("m_op_ing_otra_dep")[:1]
        )

        subq_conf_pend = (
            conf_est_meta_conf.objects
            .filter(n_anio_est=year, n_mes_est=month, n_instancia=OuterRef("n_instancia"))
            .values("m_op_pend_reserva")[:1]
        )

        return (
            mae_est_meta_resumenes.objects
            .select_related("n_id_modulo", "n_instancia", "n_instancia__c_org_jurisd")
            .filter(n_anio_est=year, n_mes_est=month)
            .annotate(
                # (opcional) de detalles febrero:
                m_t_ingreso_mes=Coalesce(Subquery(subq_febrero_detalles), Value(0), output_field=IntegerField()),
                op_egre_act=Coalesce(Subquery(subq_conf_egre), Value(0), output_field=IntegerField()),
                op_ing_act=Coalesce(Subquery(subq_conf_ing), Value(0), output_field=IntegerField()),
                op_pend_act=Coalesce(Subquery(subq_conf_pend), Value(0), output_field=IntegerField()),
            )
            .order_by("n_id_modulo_id", "n_instancia__c_org_jurisd_id", "n_instancia_id")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        month = today.month

        ctx["anio_actual"] = today.year
        ctx["mes_actual_num"] = month                  
        ctx["mes_actual_sin_feb"] = month - 1              
        ctx["meses_falta"] = 12 - month      
        return ctx

def _int_or_none(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None

@login_required
@require_POST
def meta_resumen_guardar_modificado(request, pk):
    base = get_object_or_404(mae_est_meta_resumenes, pk=pk)

    n_valor_modificado = _int_or_none(request.POST.get("n_valor_modificado"))
    n_meta_opj        = _int_or_none(request.POST.get("n_meta_opj"))

    if n_valor_modificado is None or n_meta_opj is None:
        return JsonResponse({"ok": False, "msg": "Valores inválidos."}, status=400)

    # Clave lógica para evitar duplicados: anio, mes, modulo, instancia
    obj, created = mae_est_meta_resumenes_modificado.objects.update_or_create(
        n_anio_est=base.n_anio_est,
        n_mes_est=base.n_mes_est,
        n_id_modulo=base.n_id_modulo,
        n_instancia=base.n_instancia,
        defaults={
            "m_estandar_prod": base.m_estandar_prod,
            "n_carg_procesal_ini": base.n_carg_procesal_ini,
            "m_t_resuelto": base.m_t_resuelto,
            "m_t_ingreso": base.m_t_ingreso,
            "m_t_ingreso_proy": base.m_t_ingreso_proy,
            "m_ing_proyectado": base.m_ing_proyectado,
            "m_carg_procesal_tram": base.m_carg_procesal_tram,
            "m_carg_procesal_min": base.m_carg_procesal_min,
            "m_carg_procesal_max": base.m_carg_procesal_max,
            "m_egre_otra_dep": base.m_egre_otra_dep,
            "m_ing_otra_dep": base.m_ing_otra_dep,
            "m_pend_reserva": base.m_pend_reserva,
            "m_meta_preliminar": base.m_meta_preliminar,
            "x_situacion_carga": base.x_situacion_carga,
            "m_avan_meta": base.m_avan_meta,
            "m_ideal_avan_meta": base.m_ideal_avan_meta,
            "m_ideal_avan_meta_ant": base.m_ideal_avan_meta_ant,
            "x_niv_produc": base.x_niv_produc,
            "m_niv_bueno": base.m_niv_bueno,
            "m_niv_muy_bueno": base.m_niv_muy_bueno,
            "l_estado": base.l_estado,
            "n_valor_modificado": n_valor_modificado,
            "n_meta_opj": n_meta_opj,
        }
    )

    return JsonResponse({
        "ok": True,
        "created": created,
        "msg": "Guardado correctamente",
        "n_id_meta_resumen_mod": obj.pk,
    })

@login_required
@require_POST
def meta_resumen_guardar_bulk(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        items = payload.get("items", [])
    except Exception:
        return JsonResponse({"ok": False, "msg": "JSON inválido"}, status=400)

    resultados = []
    with transaction.atomic():
        for it in items:
            pk  = it.get("pk")
            val = _int_or_none(it.get("n_valor_modificado"))
            opj_raw = it.get("n_meta_opj")
            flags = it.get("flags", {})

            if not pk:
                resultados.append({"pk": pk, "ok": False, "msg": "PK faltante"})
                continue

            base = mae_est_meta_resumenes.objects.filter(pk=pk).first()
            if not base:
                resultados.append({"pk": pk, "ok": False, "msg": "No existe"})
                continue

            # normaliza delta y opj
            if val is None:
                val = 0
            opj = _int_or_none(opj_raw) if opj_raw is not None else None

            # booleans desde flags (true/false)
            op_egre = bool(flags.get("m_op_egre_otra_dep", False))
            op_ing  = bool(flags.get("m_op_ing_otra_dep", False))
            op_pend = bool(flags.get("m_op_pend_reserva", False))

            obj, created = mae_est_meta_resumenes_modificado.objects.update_or_create(
                n_anio_est=base.n_anio_est,
                n_mes_est=base.n_mes_est,
                n_id_modulo=base.n_id_modulo,
                n_instancia=base.n_instancia,
                defaults={
                    "m_estandar_prod": base.m_estandar_prod,
                    "n_carg_procesal_ini": base.n_carg_procesal_ini,
                    "m_t_resuelto": base.m_t_resuelto,
                    "m_t_ingreso": base.m_t_ingreso,
                    "m_t_ingreso_proy": base.m_t_ingreso_proy,
                    "m_ing_proyectado": base.m_ing_proyectado,
                    "m_carg_procesal_tram": base.m_carg_procesal_tram,
                    "m_carg_procesal_min": base.m_carg_procesal_min,
                    "m_carg_procesal_max": base.m_carg_procesal_max,
                    "m_egre_otra_dep": base.m_egre_otra_dep,
                    "m_ing_otra_dep": base.m_ing_otra_dep,
                    "m_pend_reserva": base.m_pend_reserva,
                    "m_meta_preliminar": base.m_meta_preliminar + val,  # base + delta
                    "x_situacion_carga": base.x_situacion_carga,
                    "m_avan_meta": base.m_avan_meta,
                    "m_ideal_avan_meta": base.m_ideal_avan_meta,
                    "m_ideal_avan_meta_ant": base.m_ideal_avan_meta_ant,
                    "x_niv_produc": base.x_niv_produc,
                    "m_niv_bueno": base.m_niv_bueno,
                    "m_niv_muy_bueno": base.m_niv_muy_bueno,
                    "l_estado": base.l_estado,
                    "n_valor_modificado": val,
                    "n_meta_opj": opj,  # puede quedar NULL
                    # booleans
                    "m_op_egre_otra_dep": op_egre,
                    "m_op_ing_otra_dep":  op_ing,
                    "m_op_pend_reserva":  op_pend,
                }
            )
            resultados.append({"pk": pk, "ok": True, "created": created, "id_mod": obj.pk})

    return JsonResponse({"ok": True, "resultados": resultados})


#
#OPCION B
#
class MetaResumenOpcionBListView(LoginRequiredMixin, ListView):
    template_name = "est/meta_resumen_opcion_b.html"
    context_object_name = "items"

    def _get_periodo(self):
        today = timezone.localdate()  # zona horaria de tu proyecto
        # Nuevo: soporta ?period=YYYY-MM
        period = self.request.GET.get("period")
        if period:
            try:
                y, m = period.split("-")
                year = int(y)
                month = int(m)
                # sanea mes fuera de rango
                if month < 1 or month > 12:
                    raise ValueError
                return year, month
            except Exception:
                pass  # si viene mal formado, caemos a year/month/today

        # Compatibilidad: year & month por separado
        try:
            year = int(self.request.GET.get("year", today.year))
            month = int(self.request.GET.get("month", today.month))
            if month < 1 or month > 12:
                month = today.month
            return year, month
        except Exception:
            return today.year, today.month

    def get_queryset(self):
        year, month = self._get_periodo()
        self.year, self.month = year, month

        # --- Subquery: total de ingresos de FEBRERO por (anio, instancia) ---
        # Si deseas otro mes, cambia n_mes_est=2 por el que corresponda.
        subq_febrero_detalles = (
            mae_est_meta_detalles.objects
            .filter(n_anio_est=year, n_mes_est=2, n_instancia=OuterRef("n_instancia"))
            .values("n_instancia")
            .annotate(total=Sum("m_t_ingreso_mes"))
            .values("total")[:1]
        )

        # Switches configurables (para la vista base)
        subq_conf_egre = (
            conf_est_meta_conf.objects
            .filter(n_anio_est=year, n_mes_est=month, n_instancia=OuterRef("n_instancia"))
            .values("m_op_egre_otra_dep")[:1]
        )
        subq_conf_ing = (
            conf_est_meta_conf.objects
            .filter(n_anio_est=year, n_mes_est=month, n_instancia=OuterRef("n_instancia"))
            .values("m_op_ing_otra_dep")[:1]
        )
        subq_conf_pend = (
            conf_est_meta_conf.objects
            .filter(n_anio_est=year, n_mes_est=month, n_instancia=OuterRef("n_instancia"))
            .values("m_op_pend_reserva")[:1]
        )

        # ¿Existe snapshot?
        existe_snapshot = mae_est_meta_resumenes_modificado.objects.filter(
            n_anio_est=year, n_mes_est=month
        ).exists()
        self.vista = "modificado" if existe_snapshot else "base"

        if self.vista == "modificado":
            # ⬅️ AQUÍ ahora anotamos ingreso_mes_feb para que el template/JS lo tenga también en 'modificado'
            return (
                mae_est_meta_resumenes_modificado.objects
                .select_related("n_id_modulo", "n_instancia", "n_instancia__c_org_jurisd")
                .filter(n_anio_est=year, n_mes_est=month)
                .annotate(
                    ingreso_mes_feb=Coalesce(Subquery(subq_febrero_detalles), Value(0), output_field=IntegerField()),
                )
                .order_by("n_id_modulo_id", "n_instancia__c_org_jurisd_id", "n_instancia_id")
            )

        # Vista base con las mismas anotaciones que usabas
        return (
            mae_est_meta_resumenes.objects
            .select_related("n_id_modulo", "n_instancia", "n_instancia__c_org_jurisd")
            .filter(n_anio_est=year, n_mes_est=month)
            .annotate(
                m_t_ingreso_mes=Coalesce(Subquery(subq_febrero_detalles), Value(0), output_field=IntegerField()),
                op_egre_act=Coalesce(Subquery(subq_conf_egre), Value(0), output_field=IntegerField()),
                op_ing_act=Coalesce(Subquery(subq_conf_ing), Value(0), output_field=IntegerField()),
                op_pend_act=Coalesce(Subquery(subq_conf_pend), Value(0), output_field=IntegerField()),
                # Si tu template/JS esperan el alias 'ingreso_mes_feb' o 'ingajus', puedes duplicarlo:
                ingreso_mes_feb=Coalesce(Subquery(subq_febrero_detalles), Value(0), output_field=IntegerField()),
                # ing_ajustado_feb=Coalesce(Subquery(subq_febrero_detalles), Value(0), output_field=IntegerField()),
            )
            .order_by("n_id_modulo_id", "n_instancia__c_org_jurisd_id", "n_instancia_id")
        )

    def get_context_data(self, **kwargs):

        MESES_ES = ["", "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Setiembre","Octubre","Noviembre","Diciembre"]

        ctx = super().get_context_data(**kwargs)
        month = self.month
        ctx["anio_actual"] = self.year
        ctx["mes_actual_num"] = month
        ctx["mes_actual_sin_feb"] = month - 1
        ctx["meses_falta"] = 12 - month
        ctx["year"] = self.year
        ctx["month"] = self.month
        ctx["vista"] = self.vista
        ctx["mes_nombre"] = MESES_ES[month]
        return ctx

@require_POST
def crear_snapshot_temporal(request):
    try:
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
    except Exception:
        return HttpResponseBadRequest("Parámetros inválidos")

    try:
        n_creados = crear_snapshot_modificado(year, month, request.user)  # <— PASA EL USER
        return JsonResponse({'ok': True, 'creados': n_creados})
    except Exception as e:
        # Devuelve el error para que el front lo vea (mientras depuras)
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)

@transaction.atomic
def crear_snapshot_modificado(year: int, month: int, user) -> int:
    src = (mae_est_meta_resumenes.objects
           .select_related('n_id_modulo','n_instancia')
           .filter(n_anio_est=year, n_mes_est=month))

    if not src.exists():
        return 0

    # Evitar duplicados del periodo
    aud_mae_est_meta_resumenes_modificado.objects.filter(
        n_anio_est=year, n_mes_est=month
    ).delete()

    nuevos = []
    now = timezone.now()
    for s in src:
        obj = aud_mae_est_meta_resumenes_modificado(
            n_id_meta_resumen = s.n_id_meta_resumen,
            n_anio_est = s.n_anio_est,
            n_mes_est = s.n_mes_est,
            n_id_modulo = s.n_id_modulo,
            n_instancia = s.n_instancia,
            m_estandar_prod = s.m_estandar_prod,
            n_carg_procesal_ini = s.n_carg_procesal_ini,
            m_t_resuelto = s.m_t_resuelto,
            m_t_ingreso = s.m_t_ingreso,
            m_t_ingreso_proy = s.m_t_ingreso_proy,
            m_ing_proyectado = s.m_ing_proyectado,
            m_carg_procesal_tram = s.m_carg_procesal_tram,
            m_carg_procesal_min = s.m_carg_procesal_min,
            m_carg_procesal_max = s.m_carg_procesal_max,
            m_egre_otra_dep = s.m_egre_otra_dep,
            m_ing_otra_dep = s.m_ing_otra_dep,
            m_pend_reserva = s.m_pend_reserva,
            m_meta_preliminar = s.m_meta_preliminar,
            x_situacion_carga = s.x_situacion_carga,
            m_avan_meta = s.m_avan_meta,
            m_ideal_avan_meta = s.m_ideal_avan_meta,
            m_ideal_avan_meta_ant = getattr(s, 'm_ideal_avan_meta_ant', None),
            x_niv_produc = s.x_niv_produc,
            m_niv_bueno = s.m_niv_bueno,
            m_niv_muy_bueno = s.m_niv_muy_bueno,
            l_estado = 'A',
            f_fecha_mod = now,
        )
        # Auditoría de APP → b_aud = 'I' (b_trns lo pondrá el TRIGGER)
        marcar_audit(obj, user, 'I')
        nuevos.append(obj)

    aud_mae_est_meta_resumenes_modificado.objects.bulk_create(nuevos, batch_size=1000)
    return len(nuevos)

import logging
logger = logging.getLogger(__name__)

@method_decorator(require_POST, name='dispatch')  # Aplica el decorador require_POST al método dispatch de la clase (solo permite peticiones POST).
class MetaResumenGuardarBulk(View):               # Define una clase basada en vistas de Django para manejar el guardado masivo de resúmenes de metas.
    """
    Guarda en mae_est_meta_resumenes_modificado (si l_estado='T') y
    recalcula/persiste:
      - m_meta_preliminar
      - m_ing_proyectado
      - m_carg_procesal_tram
      - m_avan_meta (% con 2 decimales)
      - x_niv_produc (BAJO/BUENO/MUY BUENO)
      - m_niv_bueno
      - m_niv_muy_bueno
    """
    def post(self, request, *args, **kwargs):   
        try:
            payload = json.loads(request.body.decode('utf-8'))  
            items = payload.get('items', [])                    
        except Exception:
            return HttpResponseBadRequest("JSON inválido")      # Si falla el parseo, retorna 400 con mensaje de error.
        
        # Si no hay items, responder rápido
        if not items:
            return JsonResponse({'ok': True, 'resultados': []})

        # --- Recolectar PKs enviados desde el front ---
        pks = [it.get('pk') for it in items if it.get('pk')]
        if not pks:
            return JsonResponse({'ok': True, 'resultados': []})

        # --- Subquery: total de ingresos de FEBRERO por (anio, instancia) ---
        subq_febrero = (
            mae_est_meta_detalles.objects
            .filter(
                n_anio_est=OuterRef('n_anio_est'),
                n_mes_est=2,  # FEBRERO (ajusta si quieres otro mes)
                n_instancia=OuterRef('n_instancia')
            )
            .values('n_instancia')
            .annotate(total=Sum('m_t_ingreso_mes'))
            .values('total')[:1]
        )

        resultados = []                                         # Acumulará el resultado (por fila) para devolverlo al front.
        with transaction.atomic():                              # Abre una transacción atómica: si algo falla, se revierte todo.
            # --- Traer todos los objetos a actualizar, bloqueados y ANOTADOS con ingreso_mes_feb ---
            objs = (
                mae_est_meta_resumenes_modificado.objects
                .select_for_update()
                .filter(pk__in=pks)
                .annotate(
                    ingreso_mes_feb=Coalesce(Subquery(subq_febrero), Value(0), output_field=IntegerField()),
                )
            )
            objs_by_pk = {o.pk: o for o in objs}

            for it in items:                                    # Itera cada item (una fila de la tabla del front).
                pk = it.get('pk')                               # Lee el identificador primario de la fila a actualizar.
                if not pk:
                    resultados.append({'pk': None, 'ok': False, 'msg': 'PK faltante'})
                    continue

                obj = objs_by_pk.get(pk)
                if not obj:
                    resultados.append({'pk': pk, 'ok': False, 'msg': 'No existe en MOD'})
                    continue

                if obj.l_estado != 'T':
                    resultados.append({'pk': pk, 'ok': False, 'msg': f'Estado no editable: {obj.l_estado}'})
                    continue

                # ===========================================================================================================
                #    Actualiza campos de valor modificado y OPJ
                # ===========================================================================================================
                # n_valor_modificado (delta)
                # Si se agrega un número en valor agregado, este se convertira a Int. Caso contrario será igual a 0.
                try:
                    nuevo_delta = int(it.get('n_valor_modificado', 0)) if it.get('n_valor_modificado', 0) is not None else 0
                except:
                    nuevo_delta = 0             

                # n_meta_opj (Valor OPJ)
                # Si se agrega un valor en OPJ, se convertira a Int. Si se deja vacío, será vacio.
                opj_raw = it.get('n_meta_opj', None)
                try:
                    nuevo_opj = int(opj_raw) if opj_raw not in (None, '') else None
                except:
                    nuevo_opj = None

                # ===========================================================================================================
                #    SWITCHES (egresos/ingresos/pendiente)
                # ===========================================================================================================
                flags = it.get('flags', {})                     # Extrae el dict de flags; por defecto, vacío.
                opEgre = bool(flags.get('m_op_egre_otra_dep'))  # True/False para “egresos a otra dep.”
                opIng  = bool(flags.get('m_op_ing_otra_dep'))   # True/False para “ingresos de otra dep.”
                opPend = bool(flags.get('m_op_pend_reserva'))   # True/False para “pendiente en reserva”.

                # ===========================================================================================================
                #    
                # ===========================================================================================================
                # Delta anterior es el ultimo valor guardado en el campo VALOR_AGREGADO, sino 0.
                delta_anterior = obj.n_valor_modificado or 0    
                # Si ingresas un nuevo valor a VALOR AGREGADO, recalcula la meta preliminar.
                # m_meta_preliminar: (Monto actual de meta preliminar - delta_anterior) + delta_nuevo
                m_meta_preliminar_nueva = (obj.m_meta_preliminar - delta_anterior) + nuevo_delta
                if m_meta_preliminar_nueva < 0:
                    m_meta_preliminar_nueva = 0

                # ===========================================================================================================
                #   CAMPO DE MESES
                # ===========================================================================================================
                month = obj.n_mes_est                           
                MES_ACTUAL_SIN_FEB = max(month - 1, 0)          
                MESES_FALTA        = max(12 - month, 0)         

                #! ===========================================================================================================
                #!  
                #! ===========================================================================================================
                # OJO: aquí restas m_t_ingreso_proy. Si en el front restas "ingreso del mes actual",
                # deberías alinear este campo con el que usas en el template (p. ej. ing_ajustado_feb).
                febrero_total = obj.ingreso_mes_feb or 0
                numerador = (obj.m_t_ingreso or 0) - febrero_total

                # Aplica switches: si están activos, ajusta el numerador (restando).
                if opEgre:
                    numerador -= (obj.m_egre_otra_dep or 0)     # Resta egresos a otra dependencia si se activa el switch.
                if opIng:
                    numerador -= (obj.m_ing_otra_dep or 0)      # Resta ingresos de otra dependencia si se activa (nota: en front restas).

                # ===========================================================================================================
                #   INGRESOS PROYECTADOS : m_ing_proyectado
                #  Si((m_t_ingreso - m_t_ingreso_mes) - Si(m_op_egre_otra_dep = "1" entonces m_egre_otra_dep sino 0) - Si(m_op_ing_otra_dep = "1" entonces m_ing_otra_dep sino 0)) / mes_actual_sin_feb) * meses_falta   
                # ===========================================================================================================
                # Calcula la proyección de ingresos en base a promedio por mes y meses restantes.
                if MES_ACTUAL_SIN_FEB > 0:
                    proy = (Decimal(obj.m_t_ingreso or 0) - Decimal(febrero_total))  # tu numerador ya ajustado
                    proy = (proy / Decimal(MES_ACTUAL_SIN_FEB)) * Decimal(MESES_FALTA)
                    m_ing_proyectado_nuevo = int(proy.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
                    if m_ing_proyectado_nuevo < 0:
                        m_ing_proyectado_nuevo = 0
                else:
                    m_ing_proyectado_nuevo = 0

                # ===========================================================================================================
                #  CARGA PROCESAL
                #  M_CARG_PROCESAL_TRAM = (n_carga_procesal_ini + m_t_ingreso + m_ing_proyectado) - (m_pend_reserva * m_op_pend_reserva)
                # ===========================================================================================================
                m_carg_procesal_tram_nueva = ((obj.n_carg_procesal_ini or 0) +  (obj.m_t_ingreso or 0) + (m_ing_proyectado_nuevo or 0)) - ((obj.m_pend_reserva or 0) * (1 if opPend else 0))

                # ===========================================================================================================
                # SITUACION DE LA CARGA ( SUBCARGA / ESTANDAR / SOBRECARGA )
                # 
                # ===========================================================================================================
                min_anual = obj.m_carg_procesal_min or 0       # Límite inferior anual
                max_anual = obj.m_carg_procesal_max or 0       # Límite superior anual
                if m_carg_procesal_tram_nueva > max_anual:
                    x_situacion_carga_nueva = 'SOBRECARGA'     
                elif m_carg_procesal_tram_nueva < min_anual:
                    x_situacion_carga_nueva = 'SUBCARGA'       
                else:
                    x_situacion_carga_nueva = 'ESTANDAR'      

                # ---- m_t_resuelto_mes: suma del mes/instancia en mae_est_meta_detalles
                total_resuelto_mes = (
                    mae_est_meta_detalles.objects
                    .filter(                                     # Filtra por año, mes e instancia del registro actual
                        n_anio_est=obj.n_anio_est,
                        n_instancia=obj.n_instancia
                    )
                    .aggregate(s=Sum('m_t_resuelto_mes'))        # Suma la columna m_t_resuelto_mes
                    .get('s') or 0                               # Obtiene el total (si None, 0)
                )

                # ===========================================================================================================
                # AVANCE DE META
                # 
                # ===========================================================================================================
                # ---- m_avan_meta (%): (resuelto/meta_preliminar)*100, con 2 decimales
                if m_meta_preliminar_nueva > 0:
                    m_avan_meta = (Decimal(total_resuelto_mes) * Decimal(100)) / Decimal(m_meta_preliminar_nueva)
                    m_avan_meta = m_avan_meta.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # Redondea a 2 decimales.
                else:
                    m_avan_meta = Decimal('0.00')               # Si la meta es 0, avance = 0%.

                # ===========================================================================================================
                # NIVEL DE PRODUCTIVIDAD
                # BAJO , BUENO Y MUY BUENO
                # ===========================================================================================================
                # ---- x_niv_produc según rangos del % de avance
                # BAJO:     0.00 < m_avan_meta < 55.00
                # BUENO:    55.00 <= m_avan_meta < 64.00
                # MUY BUENO: en otro caso
                avan = m_avan_meta                               # Decimal con 2 decimales (ya redondeado)
                if avan > Decimal('0.00') and avan < Decimal('55.00'):
                    x_niv_produc = 'BAJO'
                elif avan >= Decimal('55.00') and avan < Decimal('64.00'):
                    x_niv_produc = 'BUENO'
                else:
                    x_niv_produc = 'MUY BUENO'


                # ===========================================================================================================
                # CANTIDAD PARA NIVEL BUENO Y NIVEL MUY BUENO
                # ===========================================================================================================
                # ---- m_niv_bueno y m_niv_muy_bueno usan la misma sub-fórmula auxiliar
                # Fórmula base: (resuelto / m_avan_meta) * ideal - resuelto
                # OJO: m_avan_meta está en porcentaje (0..100), por eso se divide directamente.
                def _calc_nivel(resuelto, avan_pct, ideal):
                    if avan_pct in (None, 0, Decimal('0.00')):   # Evita división entre cero.
                        return 0
                    res = Decimal(resuelto)                      # Normaliza a Decimal
                    avan_pct = Decimal(avan_pct)                 # Pasa el % actual a Decimal
                    ideal = Decimal(ideal or 0)                  # Ideal (si None, 0)
                    try:
                        valor = ((res / avan_pct) * ideal) - res # Aplica la fórmula
                    except Exception:
                        valor = Decimal('0')
                    # Redondea a entero (half up) y evita negativos
                    val_int = int(valor.to_integral_value(rounding=ROUND_HALF_UP))
                    return max(val_int, 0)

                # Calcula m_niv_bueno solo si el nivel actual es BAJO
                m_niv_bueno_nuevo = 0
                if x_niv_produc == 'BAJO':
                    m_niv_bueno_nuevo = _calc_nivel(
                        total_resuelto_mes,
                        m_avan_meta,
                        obj.m_ideal_avan_meta_ant                   # % ideal “bueno” del modelo
                    )

                # Calcula m_niv_muy_bueno si el nivel es BAJO o BUENO
                m_niv_muy_bueno_nuevo = 0
                if x_niv_produc in ('BAJO', 'BUENO'):
                    m_niv_muy_bueno_nuevo = _calc_nivel(
                        total_resuelto_mes,
                        m_avan_meta,
                        obj.m_ideal_avan_meta               # % ideal “muy bueno” (anterior/objetivo mayor)
                    )

                logger.info(
                    "GuardarBulk pk=%s | avan=%s | x_niv_produc=%s | m_niv_bueno_nuevo=%s | m_niv_muy_bueno_nuevo=%s",
                    pk, str(m_avan_meta), x_niv_produc, m_niv_bueno_nuevo, m_niv_muy_bueno_nuevo
                )

                # ---- Persistir todos los campos recalculados/recibidos
                obj.n_valor_modificado   = nuevo_delta
                obj.n_meta_opj           = nuevo_opj
                obj.m_op_egre_otra_dep   = opEgre
                obj.m_op_ing_otra_dep    = opIng
                obj.m_op_pend_reserva    = opPend
                obj.m_meta_preliminar    = m_meta_preliminar_nueva
                obj.m_ing_proyectado     = m_ing_proyectado_nuevo
                obj.m_carg_procesal_tram = m_carg_procesal_tram_nueva
                obj.m_avan_meta          = m_avan_meta
                obj.x_niv_produc         = x_niv_produc
                obj.m_niv_bueno          = m_niv_bueno_nuevo
                obj.m_niv_muy_bueno      = m_niv_muy_bueno_nuevo
                obj.x_situacion_carga    = x_situacion_carga_nueva

                

                # Guarda solo los campos listados (update_fields) y actualiza f_fecha_mod (asumo auto_now=True o lo manejas en save).
                obj.save(update_fields=[
                    'n_valor_modificado','n_meta_opj',
                    'm_op_egre_otra_dep','m_op_ing_otra_dep','m_op_pend_reserva',
                    'm_meta_preliminar','m_ing_proyectado','m_carg_procesal_tram',
                    'm_avan_meta','x_niv_produc','m_niv_bueno','m_niv_muy_bueno',
                    'x_situacion_carga', 
                    'f_fecha_mod',
                ])

                # Arma el resultado por fila para que el front pueda pintar sin recargar la página
                resultados.append({
                    'pk': pk, 'ok': True,
                    'n_valor_modificado': obj.n_valor_modificado,
                    'n_meta_opj': obj.n_meta_opj,
                    'm_meta_preliminar': obj.m_meta_preliminar,
                    'm_ing_proyectado': obj.m_ing_proyectado,
                    'm_carg_procesal_tram': obj.m_carg_procesal_tram,
                    'm_avan_meta': str(obj.m_avan_meta),   # Envía Decimal como string para evitar problemas de serialización.
                    'x_niv_produc': obj.x_niv_produc,
                    'm_niv_bueno': obj.m_niv_bueno,
                    'm_niv_muy_bueno': obj.m_niv_muy_bueno,
                    'x_situacion_carga': obj.x_situacion_carga,

                    # ---- Bloque debug extra para el front ----
                    'debug': {
                        'avan': str(m_avan_meta),
                        'x_niv_produc': x_niv_produc,
                        'm_niv_bueno_nuevo': m_niv_bueno_nuevo,
                        'm_niv_muy_bueno_nuevo': m_niv_muy_bueno_nuevo,

                        # (opcionales muy útiles para verificar cálculos)
                        'febrero_total': febrero_total,
                        'numerador': int(numerador),
                        'MES_ACTUAL_SIN_FEB': MES_ACTUAL_SIN_FEB,
                        'MESES_FALTA': MESES_FALTA,
                        'm_meta_preliminar_nueva': m_meta_preliminar_nueva,
                        'total_resuelto_mes' : total_resuelto_mes,
                        'm_ideal_avan_meta_ant': obj.m_ideal_avan_meta_ant,
                        'm_ideal_avan_meta': obj.m_ideal_avan_meta,

                    }
                })

        # Fuera del for y fuera del with (transacción ya cerró correctamente), devuelve el JSON para el front.
        return JsonResponse({'ok': True, 'resultados': resultados})

@require_POST
@transaction.atomic
def meta_resumen_cerrar_definitivo(request):
    """
    Vuelca los datos del periodo (año/mes) desde mae_est_meta_resumenes_modificado → mae_est_meta_resumenes
    y marca l_estado='C' en mae_est_meta_resumenes_modificado.
    """
    try:
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
    except Exception:
        return HttpResponseBadRequest("Parámetros inválidos")

    mods = (
        mae_est_meta_resumenes_modificado.objects
        .select_for_update()
        .filter(n_anio_est=year, n_mes_est=month, l_estado='T')
        .select_related('n_instancia', 'n_id_modulo')
    )

    campos_volcar = [
        'm_estandar_prod','n_carg_procesal_ini','m_t_resuelto','m_t_ingreso','m_t_ingreso_proy',
        'm_ing_proyectado','m_carg_procesal_tram','m_carg_procesal_min','m_carg_procesal_max',
        'm_egre_otra_dep','m_ing_otra_dep','m_pend_reserva','m_meta_preliminar','x_situacion_carga',
        'm_avan_meta','m_ideal_avan_meta','m_ideal_avan_meta_ant','x_niv_produc','m_niv_bueno','m_niv_muy_bueno',
    ]

    for m in mods:
        base_row, _ = mae_est_meta_resumenes.objects.get_or_create(
            n_anio_est=year,
            n_mes_est=month,
            n_id_modulo=m.n_id_modulo,
            n_instancia=m.n_instancia,
        )
        for f in campos_volcar:
            setattr(base_row, f, getattr(m, f))
        base_row.save(update_fields=campos_volcar)

    cerrados = mods.update(l_estado='C')
    return JsonResponse({'ok': True, 'cerrados': cerrados})

@require_POST
@transaction.atomic
def meta_resumen_volver_abrir(request):
    """
    Reabre el periodo: NO copia nada; solo marca l_estado='T' en 'modificado' (estaba 'C').
    """
    try:
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
    except Exception:
        return HttpResponseBadRequest("Parámetros inválidos")

    modulo_id = request.POST.get('modulo')  # opcional

    mods = (mae_est_meta_resumenes_modificado.objects
            .select_for_update()
            .filter(n_anio_est=year, n_mes_est=month, l_estado='C')  # solo cerrados se pueden reabrir
            .select_related('n_instancia', 'n_id_modulo'))

    if modulo_id:
        mods = mods.filter(n_id_modulo_id=modulo_id)

    abiertos = mods.update(l_estado='T')
    return JsonResponse({'ok': True, 'abiertos': abiertos})

#! ==============================================================
#! =============== CUADRO MENSUAL DE METAS ======================
#! Es el cuadro final mensual que la oficina de estadistica muestra
#! mes a mes, sobre estadisticas de los juzgados.
#! ==============================================================
from django.db.models import (
    Case, When, IntegerField, FloatField, Max, Q, F, Value as V
)
from django.db.models.functions import Coalesce

class MetaCuadroMensualView(LoginRequiredMixin, TemplateView):
    template_name = "est/metas_cuadro_mensual.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        year = today.year
        month = today.month

        # Mapeo de colores por nivel
        map_css = {"MUY BUENO": "niv-muy-bueno", "BUENO": "niv-bueno", "BAJO": "niv-bajo"}

        # ---- Aggregation helper: toma el valor del campo en el mes m (sin sumar)
        def agg_mes_int(field, m):
            # Si hay 1 fila por (instancia,mes), Max == valor
            return Max(
                Case(When(n_mes_est=m, then=field), default=None, output_field=IntegerField()),
                filter=Q(n_anio_est=year),
            )

        # ============= 1) DETALLES: una fila por instancia con res_m01..12 / ing_m01..12 ============
        det_qs = (
            mae_est_meta_detalles.objects
            .filter(n_anio_est=year)
            .values(
                "n_instancia_id",
                "n_instancia__x_nom_instancia",
                "n_instancia__c_org_jurisd__x_nom_org_jurisd",
            )
            .annotate(
                # RESUELTOS por mes
                res_m01=agg_mes_int("m_t_resuelto_mes", 1),
                res_m02=agg_mes_int("m_t_resuelto_mes", 2),
                res_m03=agg_mes_int("m_t_resuelto_mes", 3),
                res_m04=agg_mes_int("m_t_resuelto_mes", 4),
                res_m05=agg_mes_int("m_t_resuelto_mes", 5),
                res_m06=agg_mes_int("m_t_resuelto_mes", 6),
                res_m07=agg_mes_int("m_t_resuelto_mes", 7),
                res_m08=agg_mes_int("m_t_resuelto_mes", 8),
                res_m09=agg_mes_int("m_t_resuelto_mes", 9),
                res_m10=agg_mes_int("m_t_resuelto_mes",10),
                res_m11=agg_mes_int("m_t_resuelto_mes",11),
                res_m12=agg_mes_int("m_t_resuelto_mes",12),
                # INGRESOS por mes
                ing_m01=agg_mes_int("m_t_ingreso_mes", 1),
                ing_m02=agg_mes_int("m_t_ingreso_mes", 2),
                ing_m03=agg_mes_int("m_t_ingreso_mes", 3),
                ing_m04=agg_mes_int("m_t_ingreso_mes", 4),
                ing_m05=agg_mes_int("m_t_ingreso_mes", 5),
                ing_m06=agg_mes_int("m_t_ingreso_mes", 6),
                ing_m07=agg_mes_int("m_t_ingreso_mes", 7),
                ing_m08=agg_mes_int("m_t_ingreso_mes", 8),
                ing_m09=agg_mes_int("m_t_ingreso_mes", 9),
                ing_m10=agg_mes_int("m_t_ingreso_mes",10),
                ing_m11=agg_mes_int("m_t_ingreso_mes",11),
                ing_m12=agg_mes_int("m_t_ingreso_mes",12),
            )
        )
        det_por_inst = {r["n_instancia_id"]: r for r in det_qs}

        # ============= 2) RESÚMENES: niveles por mes + fijos del mes actual (una sola query) ============
        res_qs = (
            mae_est_meta_resumenes_modificado.objects
            .filter(n_anio_est=year)
            .values("n_instancia_id", "n_mes_est")
            .annotate(
                nivel=Coalesce(Max("x_niv_produc"), V("")),
                estandar=Max(Case(When(n_mes_est=month, then="m_estandar_prod"), output_field=IntegerField())),
                meta_preliminar=Max(Case(When(n_mes_est=month, then="m_meta_preliminar"), output_field=IntegerField())),
                carga_inicial=Max(Case(When(n_mes_est=month, then="n_carg_procesal_ini"), output_field=IntegerField())),
                pct_real_avance=Max(Case(When(n_mes_est=month, then="m_avan_meta"), output_field=FloatField())),
                pct_ideal_avance=Max(Case(When(n_mes_est=month, then="m_ideal_avan_meta"), output_field=IntegerField())),
                niv_bueno=Max(Case(When(n_mes_est=month, then="m_niv_bueno"), output_field=IntegerField())),
                niv_muy_bueno=Max(Case(When(n_mes_est=month, then="m_niv_muy_bueno"), output_field=IntegerField())),
            )
        )
        niveles_por_inst = {}
        fijos_mes_actual = {}
        for r in res_qs:
            inst = r["n_instancia_id"]
            m = r["n_mes_est"]
            niveles_por_inst.setdefault(inst, [""] * 12)
            niveles_por_inst[inst][m - 1] = (r["nivel"] or "").strip().upper()
            if m == month and inst not in fijos_mes_actual:
                fijos_mes_actual[inst] = {
                    "estandar": r["estandar"] or 0,
                    "meta_preliminar": r["meta_preliminar"] or 0,
                    "carga_inicial": r["carga_inicial"] or 0,
                    "pct_real_avance": r["pct_real_avance"] or 0.0,
                    "pct_ideal_avance": r["pct_ideal_avance"] or 0,
                    "nivel_prod": niveles_por_inst[inst][m - 1],
                    "niv_bueno": r["niv_bueno"] or 0,
                    "niv_muy_bueno": r["niv_muy_bueno"] or 0,
                }

        # ============= 3) ORDEN desde mov_est_instancia_modulos (módulo → n_orden) ============
        modulo_id = self.kwargs.get("modulo_id") or self.request.GET.get("modulo")
        map_qs = mov_est_instancia_modulos.objects.filter(l_activo="S")
        if modulo_id:
            map_qs = map_qs.filter(n_id_modulo_id=modulo_id)

        map_qs = (
            map_qs
            .values(
                "n_id_instancia_modulo",
                "n_id_modulo_id",
                "n_id_modulo__x_nombre",     # nombre del módulo
                "n_orden",
                "n_instancia_id",
                "n_instancia__x_nom_instancia",
                "n_instancia__c_org_jurisd__x_nom_org_jurisd",
            )
            .order_by("n_id_modulo_id", "n_orden", "n_instancia_id")
        )

        # ============= 4) JUECES por instancia (activos) ============
        inst_ids = [row["n_instancia_id"] for row in map_qs]
        
        jueces_qs = (
            mov_est_instancia_jueces.objects
            .filter(l_activo="S", n_instancia_id__in=inst_ids)
            .select_related('n_id_juez__usuario')
            .values(
                "n_instancia_id",
                "n_id_juez__usuario__x_nombres",
                "n_id_juez__usuario__x_app_paterno", 
                "n_id_juez__usuario__x_app_materno",
                "n_id_juez__usuario__x_telefono",
                "n_id_juez__usuario__l_mensaje",
                "n_id_juez__usuario__n_id_sexo__x_descripcion"
            )
            .order_by("n_instancia_id", "n_id_juez_id")
        )
        
        # Mapa instancia -> lista de nombres (para compatibilidad)
        # Mapa instancia -> lista de objetos juez (nuevo formato)
        jueces_por_inst = {}
        jueces_objetos_por_inst = {}
        
        for r in jueces_qs:
            inst = r["n_instancia_id"]
            nombres = r["n_id_juez__usuario__x_nombres"] or ""
            apellido_paterno = r["n_id_juez__usuario__x_app_paterno"] or ""
            apellido_materno = r["n_id_juez__usuario__x_app_materno"] or ""
            telefono = r["n_id_juez__usuario__x_telefono"]
            l_mensaje = r["n_id_juez__usuario__l_mensaje"]
            sexo = r["n_id_juez__usuario__n_id_sexo__x_descripcion"]
            
            # Construir nombre completo
            nombre_completo = f"{apellido_paterno} {apellido_materno}, {nombres}".strip(" ,")
            
            if nombre_completo and nombre_completo != ",":
                # Para compatibilidad: lista de nombres separados por " · "
                jueces_por_inst.setdefault(inst, [])
                if nombre_completo not in jueces_por_inst[inst]:
                    jueces_por_inst[inst].append(nombre_completo)
                
                # Nuevo formato: objetos con nombre y número
                jueces_objetos_por_inst.setdefault(inst, [])
                juez_obj = {
                    "nombre_completo": nombre_completo,
                    "telefono": telefono,
                    "l_mensaje": l_mensaje,
                    "sexo": sexo
                }
                if juez_obj not in jueces_objetos_por_inst[inst]:
                    jueces_objetos_por_inst[inst].append(juez_obj)

        # ============= 5) Mezclar todo en filas en el ORDEN pedido ============
        filas = []
        for mrow in map_qs:
            inst_id = mrow["n_instancia_id"]
            det = det_por_inst.get(inst_id)

            if det:
                res_vals = [det.get(f"res_m{mm:02d}") or 0 for mm in range(1, 13)]
                ing_vals = [det.get(f"ing_m{mm:02d}") or 0 for mm in range(1, 13)]
                org = det["n_instancia__c_org_jurisd__x_nom_org_jurisd"]
                inst_nom = det["n_instancia__x_nom_instancia"]
            else:
                res_vals = [0] * 12
                ing_vals = [0] * 12
                org = mrow["n_instancia__c_org_jurisd__x_nom_org_jurisd"]
                inst_nom = mrow["n_instancia__x_nom_instancia"]

            niveles = niveles_por_inst.get(inst_id, [""] * 12)
            clases = [map_css.get(n, "") for n in niveles]
            res_cells = [{"val": res_vals[i], "cls": clases[i], "nivel": niveles[i]} for i in range(12)]
            ing_cells = [{"val": ing_vals[i], "cls": clases[i], "nivel": niveles[i]} for i in range(12)]

            fijos = fijos_mes_actual.get(inst_id, {
                "estandar": 0, "meta_preliminar": 0, "carga_inicial": 0,
                "pct_real_avance": 0.0, "pct_ideal_avance": 0,
                "nivel_prod": "", "niv_bueno": 0, "niv_muy_bueno": 0
            })

            filas.append({
                "org_jurisd": org,
                "instancia": inst_nom,
                "jueces": " · ".join(jueces_por_inst.get(inst_id, [])),
                "jueces_objetos": jueces_objetos_por_inst.get(inst_id, []),  # <-- NUEVO: objetos con nombre, teléfono, l_mensaje y sexo  # <-- NUEVO
                "jueces_objetos": jueces_objetos_por_inst.get(inst_id, []),  # <-- NUEVO: objetos con nombre, teléfono, l_mensaje y sexo
                "estandar": fijos["estandar"],
                "meta_preliminar": fijos["meta_preliminar"],
                "carga_inicial": fijos["carga_inicial"],
                "pct_real_avance": fijos["pct_real_avance"],
                "pct_ideal_avance": fijos["pct_ideal_avance"],
                "nivel_prod": fijos["nivel_prod"],
                "niv_bueno": fijos["niv_bueno"],
                "niv_muy_bueno": fijos["niv_muy_bueno"],
                "res_cells": res_cells,
                "ing_cells": ing_cells,
                "res_total": sum(res_vals),
                "ing_total": sum(ing_vals),

                # Para separadores por módulo en el template
                "modulo_id": mrow["n_id_modulo_id"],
                "modulo_nom": mrow["n_id_modulo__x_nombre"],
                "n_orden": mrow["n_orden"],
            })

        # columnas totales (ajústalo según tu tabla para el separador azul)
        ctx["colspan"] = 24
        ctx["anio"] = year
        ctx["mes_actual"] = month
        ctx["filas"] = filas
        ctx["meses"] = ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SET","OCT","NOV","DIC"]
        return ctx

#Antonio inicio
class MetaCuadroMensualJSONView(LoginRequiredMixin, View):
    """
    Endpoint JSON que devuelve los mismos datos que MetaCuadroMensualView
    pero en formato JSON para consumo de APIs
    """
    
    def get(self, request):
        today = timezone.localdate()
        year = today.year
        month = today.month
        
        # Permitir especificar año y mes por parámetros
        if 'year' in request.GET:
            try:
                year = int(request.GET.get('year'))
            except (ValueError, TypeError):
                year = today.year
                
        if 'month' in request.GET:
            try:
                month = int(request.GET.get('month'))
                if month < 1 or month > 12:
                    month = today.month
            except (ValueError, TypeError):
                month = today.month

        # Mapeo de colores por nivel
        map_css = {"MUY BUENO": "niv-muy-bueno", "BUENO": "niv-bueno", "BAJO": "niv-bajo"}

        # ---- Aggregation helper: toma el valor del campo en el mes m (sin sumar)
        def agg_mes_int(field, m):
            # Si hay 1 fila por (instancia,mes), Max == valor
            return Max(
                Case(When(n_mes_est=m, then=field), default=None, output_field=IntegerField()),
                filter=Q(n_anio_est=year),
            )

        # ============= 1) DETALLES: una fila por instancia con res_m01..12 / ing_m01..12 ============
        det_qs = (
            mae_est_meta_detalles.objects
            .filter(n_anio_est=year)
            .values(
                "n_instancia_id",
                "n_instancia__x_nom_instancia",
                "n_instancia__c_org_jurisd__x_nom_org_jurisd",
            )
            .annotate(
                # RESUELTOS por mes
                res_m01=agg_mes_int("m_t_resuelto_mes", 1),
                res_m02=agg_mes_int("m_t_resuelto_mes", 2),
                res_m03=agg_mes_int("m_t_resuelto_mes", 3),
                res_m04=agg_mes_int("m_t_resuelto_mes", 4),
                res_m05=agg_mes_int("m_t_resuelto_mes", 5),
                res_m06=agg_mes_int("m_t_resuelto_mes", 6),
                res_m07=agg_mes_int("m_t_resuelto_mes", 7),
                res_m08=agg_mes_int("m_t_resuelto_mes", 8),
                res_m09=agg_mes_int("m_t_resuelto_mes", 9),
                res_m10=agg_mes_int("m_t_resuelto_mes",10),
                res_m11=agg_mes_int("m_t_resuelto_mes",11),
                res_m12=agg_mes_int("m_t_resuelto_mes",12),
                # INGRESOS por mes
                ing_m01=agg_mes_int("m_t_ingreso_mes", 1),
                ing_m02=agg_mes_int("m_t_ingreso_mes", 2),
                ing_m03=agg_mes_int("m_t_ingreso_mes", 3),
                ing_m04=agg_mes_int("m_t_ingreso_mes", 4),
                ing_m05=agg_mes_int("m_t_ingreso_mes", 5),
                ing_m06=agg_mes_int("m_t_ingreso_mes", 6),
                ing_m07=agg_mes_int("m_t_ingreso_mes", 7),
                ing_m08=agg_mes_int("m_t_ingreso_mes", 8),
                ing_m09=agg_mes_int("m_t_ingreso_mes", 9),
                ing_m10=agg_mes_int("m_t_ingreso_mes",10),
                ing_m11=agg_mes_int("m_t_ingreso_mes",11),
                ing_m12=agg_mes_int("m_t_ingreso_mes",12),
            )
        )
        det_por_inst = {r["n_instancia_id"]: r for r in det_qs}

        # ============= 2) RESÚMENES: niveles por mes + fijos del mes actual (una sola query) ============
        res_qs = (
            mae_est_meta_resumenes_modificado.objects
            .filter(n_anio_est=year)
            .values("n_instancia_id", "n_mes_est")
            .annotate(
                nivel=Coalesce(Max("x_niv_produc"), V("")),
                estandar=Max(Case(When(n_mes_est=month, then="m_estandar_prod"), output_field=IntegerField())),
                meta_preliminar=Max(Case(When(n_mes_est=month, then="m_meta_preliminar"), output_field=IntegerField())),
                carga_inicial=Max(Case(When(n_mes_est=month, then="n_carg_procesal_ini"), output_field=IntegerField())),
                pct_real_avance=Max(Case(When(n_mes_est=month, then="m_avan_meta"), output_field=FloatField())),
                pct_ideal_avance=Max(Case(When(n_mes_est=month, then="m_ideal_avan_meta"), output_field=IntegerField())),
                niv_bueno=Max(Case(When(n_mes_est=month, then="m_niv_bueno"), output_field=IntegerField())),
                niv_muy_bueno=Max(Case(When(n_mes_est=month, then="m_niv_muy_bueno"), output_field=IntegerField())),
            )
        )
        niveles_por_inst = {}
        fijos_mes_actual = {}
        for r in res_qs:
            inst = r["n_instancia_id"]
            m = r["n_mes_est"]
            niveles_por_inst.setdefault(inst, [""] * 12)
            niveles_por_inst[inst][m - 1] = (r["nivel"] or "").strip().upper()
            if m == month and inst not in fijos_mes_actual:
                fijos_mes_actual[inst] = {
                    "estandar": r["estandar"] or 0,
                    "meta_preliminar": r["meta_preliminar"] or 0,
                    "carga_inicial": r["carga_inicial"] or 0,
                    "pct_real_avance": r["pct_real_avance"] or 0.0,
                    "pct_ideal_avance": r["pct_ideal_avance"] or 0,
                    "nivel_prod": niveles_por_inst[inst][m - 1],
                    "niv_bueno": r["niv_bueno"] or 0,
                    "niv_muy_bueno": r["niv_muy_bueno"] or 0,
                }

        # ============= 3) ORDEN desde mov_est_instancia_modulos (módulo → n_orden) ============
        modulo_id = request.GET.get("modulo")
        map_qs = mov_est_instancia_modulos.objects.filter(l_activo="S")
        if modulo_id:
            map_qs = map_qs.filter(n_id_modulo_id=modulo_id)

        map_qs = (
            map_qs
            .values(
                "n_id_instancia_modulo",
                "n_id_modulo_id",
                "n_id_modulo__x_nombre",     # nombre del módulo
                "n_orden",
                "n_instancia_id",
                "n_instancia__x_nom_instancia",
                "n_instancia__c_org_jurisd__x_nom_org_jurisd",
            )
            .order_by("n_id_modulo_id", "n_orden", "n_instancia_id")
        )

        # ============= 4) JUECES por instancia (activos) ============
        inst_ids = [row["n_instancia_id"] for row in map_qs]
        
        jueces_qs = (
            mov_est_instancia_jueces.objects
            .filter(l_activo="S", n_instancia_id__in=inst_ids)
            .select_related('n_id_juez__usuario')
            .values(
                "n_instancia_id",
                "n_id_juez__usuario__x_nombres",
                "n_id_juez__usuario__x_app_paterno", 
                "n_id_juez__usuario__x_app_materno",
                "n_id_juez__usuario__x_telefono",
                "n_id_juez__usuario__l_mensaje",
                "n_id_juez__usuario__n_id_sexo__x_descripcion"
            )
            .order_by("n_instancia_id", "n_id_juez_id")
        )
        
        # Mapa instancia -> lista de nombres (para compatibilidad)
        # Mapa instancia -> lista de objetos juez (nuevo formato)
        jueces_por_inst = {}
        jueces_objetos_por_inst = {}
        
        for r in jueces_qs:
            inst = r["n_instancia_id"]
            nombres = r["n_id_juez__usuario__x_nombres"] or ""
            apellido_paterno = r["n_id_juez__usuario__x_app_paterno"] or ""
            apellido_materno = r["n_id_juez__usuario__x_app_materno"] or ""
            telefono = r["n_id_juez__usuario__x_telefono"]
            l_mensaje = r["n_id_juez__usuario__l_mensaje"]
            sexo = r["n_id_juez__usuario__n_id_sexo__x_descripcion"]
            
            # Construir nombre completo
            nombre_completo = f"{apellido_paterno} {apellido_materno}, {nombres}".strip(" ,")
            
            if nombre_completo and nombre_completo != ",":
                # Para compatibilidad: lista de nombres separados por " · "
                jueces_por_inst.setdefault(inst, [])
                if nombre_completo not in jueces_por_inst[inst]:
                    jueces_por_inst[inst].append(nombre_completo)
                
                # Nuevo formato: objetos con nombre y número
                jueces_objetos_por_inst.setdefault(inst, [])
                juez_obj = {
                    "nombre_completo": nombre_completo,
                    "telefono": telefono,
                    "l_mensaje": l_mensaje,
                    "sexo": sexo
                }
                if juez_obj not in jueces_objetos_por_inst[inst]:
                    jueces_objetos_por_inst[inst].append(juez_obj)

        # ============= 5) Mezclar todo en filas en el ORDEN pedido ============
        filas = []
        for mrow in map_qs:
            inst_id = mrow["n_instancia_id"]
            det = det_por_inst.get(inst_id)

            if det:
                res_vals = [det.get(f"res_m{mm:02d}") or 0 for mm in range(1, 13)]
                ing_vals = [det.get(f"ing_m{mm:02d}") or 0 for mm in range(1, 13)]
                org = det["n_instancia__c_org_jurisd__x_nom_org_jurisd"]
                inst_nom = det["n_instancia__x_nom_instancia"]
            else:
                res_vals = [0] * 12
                ing_vals = [0] * 12
                org = mrow["n_instancia__c_org_jurisd__x_nom_org_jurisd"]
                inst_nom = mrow["n_instancia__x_nom_instancia"]

            niveles = niveles_por_inst.get(inst_id, [""] * 12)
            clases = [map_css.get(n, "") for n in niveles]
            res_cells = [{"val": res_vals[i], "cls": clases[i], "nivel": niveles[i]} for i in range(12)]
            ing_cells = [{"val": ing_vals[i], "cls": clases[i], "nivel": niveles[i]} for i in range(12)]

            fijos = fijos_mes_actual.get(inst_id, {
                "estandar": 0, "meta_preliminar": 0, "carga_inicial": 0,
                "pct_real_avance": 0.0, "pct_ideal_avance": 0,
                "nivel_prod": "", "niv_bueno": 0, "niv_muy_bueno": 0
            })

            filas.append({
                "org_jurisd": org,
                "instancia": inst_nom,
                "jueces": " · ".join(jueces_por_inst.get(inst_id, [])),
                "jueces_objetos": jueces_objetos_por_inst.get(inst_id, []),  # <-- NUEVO: objetos con nombre, teléfono, l_mensaje y sexo
                "estandar": fijos["estandar"],
                "meta_preliminar": fijos["meta_preliminar"],
                "carga_inicial": fijos["carga_inicial"],
                "pct_real_avance": fijos["pct_real_avance"],
                "pct_ideal_avance": fijos["pct_ideal_avance"],
                "nivel_prod": fijos["nivel_prod"],
                "niv_bueno": fijos["niv_bueno"],
                "niv_muy_bueno": fijos["niv_muy_bueno"],
                "res_cells": res_cells,
                "ing_cells": ing_cells,
                "res_total": sum(res_vals),
                "ing_total": sum(ing_vals),

                # Para separadores por módulo
                "modulo_id": mrow["n_id_modulo_id"],
                "modulo_nom": mrow["n_id_modulo__x_nombre"],
                "n_orden": mrow["n_orden"],
            })

        # Preparar respuesta JSON
        response_data = {
            "anio": year,
            "mes_actual": month,
            "meses": ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SET","OCT","NOV","DIC"],
            "filas": filas,
            "total_filas": len(filas),
            "fecha_consulta": today.isoformat()
        }
        
        return JsonResponse(response_data, safe=False)


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(View):
    """
    Endpoint para autenticación API que devuelve un token de sesión
    """
    
    def post(self, request):
        from django.contrib.auth import authenticate
        from django.contrib.sessions.models import Session
        import uuid
        import json
        
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return JsonResponse({
                    'success': False,
                    'error': 'Username y password son requeridos'
                }, status=400)
            
            # Autenticar usuario
            user = authenticate(username=username, password=password)
            
            if user is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Credenciales inválidas'
                }, status=401)
            
            if not user.is_active:
                return JsonResponse({
                    'success': False,
                    'error': 'Usuario inactivo'
                }, status=401)
            
            # Crear sesión manualmente
            session_key = str(uuid.uuid4())
            request.session.create()
            request.session['_auth_user_id'] = str(user.id)
            request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
            request.session.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Autenticación exitosa',
                'session_key': request.session.session_key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': getattr(user, 'email', ''),
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', '')
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class MetaCuadroMensualJSONPublicView(View):
    """
    Endpoint JSON público que NO requiere autenticación
    Útil para pruebas o integraciones externas
    """
    
    def get(self, request):
        # Verificar si hay parámetros de autenticación básica
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Basic '):
            import base64
            try:
                credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
                username, password = credentials.split(':', 1)
                
                from django.contrib.auth import authenticate
                user = authenticate(username=username, password=password)
                if not user or not user.is_active:
                    return JsonResponse({
                        'error': 'Credenciales inválidas'
                    }, status=401)
            except:
                return JsonResponse({
                    'error': 'Formato de autenticación inválido'
                }, status=401)
        else:
            # Si no hay autenticación, devolver error
            return JsonResponse({
                'error': 'Autenticación requerida. Use Basic Auth o el endpoint /est/api/login/'
            }, status=401)
        
        # Usar la misma lógica que MetaCuadroMensualJSONView
        return self._get_data(request)
    
    def _get_data(self, request):
        """Lógica compartida para obtener los datos"""
        today = timezone.localdate()
        year = today.year
        month = today.month
        
        # Permitir especificar año y mes por parámetros
        if 'year' in request.GET:
            try:
                year = int(request.GET.get('year'))
            except (ValueError, TypeError):
                year = today.year
                
        if 'month' in request.GET:
            try:
                month = int(request.GET.get('month'))
                if month < 1 or month > 12:
                    month = today.month
            except (ValueError, TypeError):
                month = today.month

        # Mapeo de colores por nivel
        map_css = {"MUY BUENO": "niv-muy-bueno", "BUENO": "niv-bueno", "BAJO": "niv-bajo"}

        # ---- Aggregation helper: toma el valor del campo en el mes m (sin sumar)
        def agg_mes_int(field, m):
            # Si hay 1 fila por (instancia,mes), Max == valor
            return Max(
                Case(When(n_mes_est=m, then=field), default=None, output_field=IntegerField()),
                filter=Q(n_anio_est=year),
            )

        # ============= 1) DETALLES: una fila por instancia con res_m01..12 / ing_m01..12 ============
        det_qs = (
            mae_est_meta_detalles.objects
            .filter(n_anio_est=year)
            .values(
                "n_instancia_id",
                "n_instancia__x_nom_instancia",
                "n_instancia__c_org_jurisd__x_nom_org_jurisd",
            )
            .annotate(
                # RESUELTOS por mes
                res_m01=agg_mes_int("m_t_resuelto_mes", 1),
                res_m02=agg_mes_int("m_t_resuelto_mes", 2),
                res_m03=agg_mes_int("m_t_resuelto_mes", 3),
                res_m04=agg_mes_int("m_t_resuelto_mes", 4),
                res_m05=agg_mes_int("m_t_resuelto_mes", 5),
                res_m06=agg_mes_int("m_t_resuelto_mes", 6),
                res_m07=agg_mes_int("m_t_resuelto_mes", 7),
                res_m08=agg_mes_int("m_t_resuelto_mes", 8),
                res_m09=agg_mes_int("m_t_resuelto_mes", 9),
                res_m10=agg_mes_int("m_t_resuelto_mes",10),
                res_m11=agg_mes_int("m_t_resuelto_mes",11),
                res_m12=agg_mes_int("m_t_resuelto_mes",12),
                # INGRESOS por mes
                ing_m01=agg_mes_int("m_t_ingreso_mes", 1),
                ing_m02=agg_mes_int("m_t_ingreso_mes", 2),
                ing_m03=agg_mes_int("m_t_ingreso_mes", 3),
                ing_m04=agg_mes_int("m_t_ingreso_mes", 4),
                ing_m05=agg_mes_int("m_t_ingreso_mes", 5),
                ing_m06=agg_mes_int("m_t_ingreso_mes", 6),
                ing_m07=agg_mes_int("m_t_ingreso_mes", 7),
                ing_m08=agg_mes_int("m_t_ingreso_mes", 8),
                ing_m09=agg_mes_int("m_t_ingreso_mes", 9),
                ing_m10=agg_mes_int("m_t_ingreso_mes",10),
                ing_m11=agg_mes_int("m_t_ingreso_mes",11),
                ing_m12=agg_mes_int("m_t_ingreso_mes",12),
            )
        )
        det_por_inst = {r["n_instancia_id"]: r for r in det_qs}

        # ============= 2) RESÚMENES: niveles por mes + fijos del mes actual (una sola query) ============
        res_qs = (
            mae_est_meta_resumenes_modificado.objects
            .filter(n_anio_est=year)
            .values("n_instancia_id", "n_mes_est")
            .annotate(
                nivel=Coalesce(Max("x_niv_produc"), V("")),
                estandar=Max(Case(When(n_mes_est=month, then="m_estandar_prod"), output_field=IntegerField())),
                meta_preliminar=Max(Case(When(n_mes_est=month, then="m_meta_preliminar"), output_field=IntegerField())),
                carga_inicial=Max(Case(When(n_mes_est=month, then="n_carg_procesal_ini"), output_field=IntegerField())),
                pct_real_avance=Max(Case(When(n_mes_est=month, then="m_avan_meta"), output_field=FloatField())),
                pct_ideal_avance=Max(Case(When(n_mes_est=month, then="m_ideal_avan_meta"), output_field=IntegerField())),
                niv_bueno=Max(Case(When(n_mes_est=month, then="m_niv_bueno"), output_field=IntegerField())),
                niv_muy_bueno=Max(Case(When(n_mes_est=month, then="m_niv_muy_bueno"), output_field=IntegerField())),
            )
        )
        niveles_por_inst = {}
        fijos_mes_actual = {}
        for r in res_qs:
            inst = r["n_instancia_id"]
            m = r["n_mes_est"]
            niveles_por_inst.setdefault(inst, [""] * 12)
            niveles_por_inst[inst][m - 1] = (r["nivel"] or "").strip().upper()
            if m == month and inst not in fijos_mes_actual:
                fijos_mes_actual[inst] = {
                    "estandar": r["estandar"] or 0,
                    "meta_preliminar": r["meta_preliminar"] or 0,
                    "carga_inicial": r["carga_inicial"] or 0,
                    "pct_real_avance": r["pct_real_avance"] or 0.0,
                    "pct_ideal_avance": r["pct_ideal_avance"] or 0,
                    "nivel_prod": niveles_por_inst[inst][m - 1],
                    "niv_bueno": r["niv_bueno"] or 0,
                    "niv_muy_bueno": r["niv_muy_bueno"] or 0,
                }

        # ============= 3) ORDEN desde mov_est_instancia_modulos (módulo → n_orden) ============
        modulo_id = request.GET.get("modulo")
        map_qs = mov_est_instancia_modulos.objects.filter(l_activo="S")
        if modulo_id:
            map_qs = map_qs.filter(n_id_modulo_id=modulo_id)

        map_qs = (
            map_qs
            .values(
                "n_id_instancia_modulo",
                "n_id_modulo_id",
                "n_id_modulo__x_nombre",     # nombre del módulo
                "n_orden",
                "n_instancia_id",
                "n_instancia__x_nom_instancia",
                "n_instancia__c_org_jurisd__x_nom_org_jurisd",
            )
            .order_by("n_id_modulo_id", "n_orden", "n_instancia_id")
        )

        # ============= 4) JUECES por instancia (activos) ============
        inst_ids = [row["n_instancia_id"] for row in map_qs]
        
        jueces_qs = (
            mov_est_instancia_jueces.objects
            .filter(l_activo="S", n_instancia_id__in=inst_ids)
            .select_related('n_id_juez__usuario')
            .values(
                "n_instancia_id",
                "n_id_juez__usuario__x_nombres",
                "n_id_juez__usuario__x_app_paterno", 
                "n_id_juez__usuario__x_app_materno",
                "n_id_juez__usuario__x_telefono",
                "n_id_juez__usuario__l_mensaje",
                "n_id_juez__usuario__n_id_sexo__x_descripcion"
            )
            .order_by("n_instancia_id", "n_id_juez_id")
        )
        
        # Mapa instancia -> lista de nombres (para compatibilidad)
        # Mapa instancia -> lista de objetos juez (nuevo formato)
        jueces_por_inst = {}
        jueces_objetos_por_inst = {}
        
        for r in jueces_qs:
            inst = r["n_instancia_id"]
            nombres = r["n_id_juez__usuario__x_nombres"] or ""
            apellido_paterno = r["n_id_juez__usuario__x_app_paterno"] or ""
            apellido_materno = r["n_id_juez__usuario__x_app_materno"] or ""
            telefono = r["n_id_juez__usuario__x_telefono"]
            l_mensaje = r["n_id_juez__usuario__l_mensaje"]
            sexo = r["n_id_juez__usuario__n_id_sexo__x_descripcion"]
            
            # Construir nombre completo
            nombre_completo = f"{apellido_paterno} {apellido_materno}, {nombres}".strip(" ,")
            
            if nombre_completo and nombre_completo != ",":
                # Para compatibilidad: lista de nombres separados por " · "
                jueces_por_inst.setdefault(inst, [])
                if nombre_completo not in jueces_por_inst[inst]:
                    jueces_por_inst[inst].append(nombre_completo)
                
                # Nuevo formato: objetos con nombre y número
                jueces_objetos_por_inst.setdefault(inst, [])
                juez_obj = {
                    "nombre_completo": nombre_completo,
                    "telefono": telefono,
                    "l_mensaje": l_mensaje,
                    "sexo": sexo
                }
                if juez_obj not in jueces_objetos_por_inst[inst]:
                    jueces_objetos_por_inst[inst].append(juez_obj)

        # ============= 5) Mezclar todo en filas en el ORDEN pedido ============
        filas = []
        for mrow in map_qs:
            inst_id = mrow["n_instancia_id"]
            det = det_por_inst.get(inst_id)

            if det:
                res_vals = [det.get(f"res_m{mm:02d}") or 0 for mm in range(1, 13)]
                ing_vals = [det.get(f"ing_m{mm:02d}") or 0 for mm in range(1, 13)]
                org = det["n_instancia__c_org_jurisd__x_nom_org_jurisd"]
                inst_nom = det["n_instancia__x_nom_instancia"]
            else:
                res_vals = [0] * 12
                ing_vals = [0] * 12
                org = mrow["n_instancia__c_org_jurisd__x_nom_org_jurisd"]
                inst_nom = mrow["n_instancia__x_nom_instancia"]

            niveles = niveles_por_inst.get(inst_id, [""] * 12)
            clases = [map_css.get(n, "") for n in niveles]
            res_cells = [{"val": res_vals[i], "cls": clases[i], "nivel": niveles[i]} for i in range(12)]
            ing_cells = [{"val": ing_vals[i], "cls": clases[i], "nivel": niveles[i]} for i in range(12)]

            fijos = fijos_mes_actual.get(inst_id, {
                "estandar": 0, "meta_preliminar": 0, "carga_inicial": 0,
                "pct_real_avance": 0.0, "pct_ideal_avance": 0,
                "nivel_prod": "", "niv_bueno": 0, "niv_muy_bueno": 0
            })

            filas.append({
                "org_jurisd": org,
                "instancia": inst_nom,
                "jueces": " · ".join(jueces_por_inst.get(inst_id, [])),
                "jueces_objetos": jueces_objetos_por_inst.get(inst_id, []),  # <-- NUEVO: objetos con nombre, teléfono, l_mensaje y sexo
                "estandar": fijos["estandar"],
                "meta_preliminar": fijos["meta_preliminar"],
                "carga_inicial": fijos["carga_inicial"],
                "pct_real_avance": fijos["pct_real_avance"],
                "pct_ideal_avance": fijos["pct_ideal_avance"],
                "nivel_prod": fijos["nivel_prod"],
                "niv_bueno": fijos["niv_bueno"],
                "niv_muy_bueno": fijos["niv_muy_bueno"],
                "res_cells": res_cells,
                "ing_cells": ing_cells,
                "res_total": sum(res_vals),
                "ing_total": sum(ing_vals),

                # Para separadores por módulo
                "modulo_id": mrow["n_id_modulo_id"],
                "modulo_nom": mrow["n_id_modulo__x_nombre"],
                "n_orden": mrow["n_orden"],
            })

        # Preparar respuesta JSON
        response_data = {
            "anio": year,
            "mes_actual": month,
            "meses": ["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SET","OCT","NOV","DIC"],
            "filas": filas,
            "total_filas": len(filas),
            "fecha_consulta": today.isoformat()
        }
        
        return JsonResponse(response_data, safe=False)

#Antonio inicio
@method_decorator(csrf_exempt, name='dispatch')
class HomeDashboardJSONView(View):
    """
    Endpoint JSON que devuelve todos los datos del dashboard home
    Basado en la sesión del usuario autenticado
    """
    #Antonio inicio
    def get(self, request):
        # Verificar autenticación Basic Auth
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Basic '):
            import base64
            try:
                credentials = base64.b64decode(auth_header[6:]).decode('utf-8')
                username, password = credentials.split(':', 1)
                
                from django.contrib.auth import authenticate
                user = authenticate(username=username, password=password)
                if not user or not user.is_active:
                    return JsonResponse({
                        'error': 'Credenciales inválidas'
                    }, status=401)
            except:
                return JsonResponse({
                    'error': 'Formato de autenticación inválido'
                }, status=401)
        else:
            # Si no hay autenticación, devolver error
            return JsonResponse({
                'error': 'Autenticación requerida. Use Basic Auth o el endpoint /est/api/login/'
            }, status=401)
        from django.utils import timezone
        from datetime import timedelta
        from django.utils.timezone import make_aware
        
        # Usar el usuario autenticado (ya está definido en la autenticación)
        #Antonio cierre
        
        # Datos básicos del usuario
        user_data = {
            'id': user.id,
            'username': user.username,
            'nombres': getattr(user, 'x_nombres', ''),
            'apellido_paterno': getattr(user, 'x_app_paterno', ''),
            'apellido_materno': getattr(user, 'x_app_materno', ''),
            'email': getattr(user, 'email', ''),
            'profile_image': user.profile_image.url if hasattr(user, 'profile_image') and user.profile_image else None,
            'is_juez': False,
            'is_admin': False
        }
        
        # Verificar permisos
        user_data['is_admin'] = user.has_perm('est.list_mae_est_modulos')
        user_data['is_juez'] = user.has_perm('est.list_mae_est_jueces')
        user_data['is_organo'] = user.has_perm('est.list_mae_est_organo_jurisdiccionales')
        
        # Contadores generales
        estadisticas_generales = {
            'cantidad_jueces_activos': mae_est_jueces.objects.filter(l_activo='S').count(),
            'cantidad_instancias': mae_est_instancia.objects.filter(l_ind_baja='N').count()
        }
        
        # Datos específicos del juez
        juez_data = None
        resumenes = []
        avance_meta = 0
        ideal_meta = 0
        
        # Verificar si es juez
        juez = mae_est_jueces.objects.filter(usuario=user, l_activo='S').first()
        
        if juez:
            user_data['is_juez'] = True
            
            # Obtener instancias asignadas al juez
            instancias_asignadas = mov_est_instancia_jueces.objects.filter(
                n_id_juez=juez, l_activo='S'
            ).select_related('n_instancia')
            
            instancias_data = [
                {
                    'id': instancia.n_instancia.n_instancia_id,
                    'nombre': instancia.n_instancia.x_nom_instancia,
                }
                for instancia in instancias_asignadas
            ]
            
            # Calcular fecha del día anterior
            fecha_actual = timezone.now()
            fecha_ayer = fecha_actual - timedelta(days=1)
            
            # Obtener resúmenes del día anterior
            resumenes_qs = mae_est_meta_resumenes.objects.filter(
                n_instancia__in=[instancia.n_instancia for instancia in instancias_asignadas],
                n_anio_est=fecha_ayer.year,
                n_mes_est=fecha_ayer.month
            ).select_related('n_instancia')
            
            resumenes = [
                {
                    'id': resumen.n_id_meta_resumen,
                    'instancia': resumen.n_instancia.x_nom_instancia,
                    'anio': resumen.n_anio_est,
                    'mes': resumen.n_mes_est,
                    'produccion': resumen.m_estandar_prod,
                    'ideal_meta': resumen.m_ideal_avan_meta,
                    'situacion_carga': resumen.x_situacion_carga,
                    'nivel_produc': resumen.x_niv_produc,
                    'ingresos': resumen.m_t_ingreso,
                    'resueltos': resumen.m_t_resuelto,
                    'IER': round((resumen.m_t_resuelto / resumen.m_t_ingreso) * 100, 2) if resumen.m_t_ingreso > 0 else 0,
                    'm_avance_meta': resumen.m_avan_meta,
                }
                for resumen in resumenes_qs
            ]
            
            # Calcular avance de meta
            if resumenes_qs:
                avance_meta = resumenes_qs.first().m_avan_meta
                ideal_meta = resumenes_qs.first().m_ideal_avan_meta
            
            juez_data = {
                'instancias_asignadas': instancias_data,
                'resumenes': resumenes,
                'avance_meta': avance_meta,
                'ideal_meta': ideal_meta,
                'fecha_consulta': fecha_ayer.isoformat()
            }
        
        # Fecha de última actualización
        try:
            meta_resumen = mae_est_meta_resumenes.objects.get(n_id_meta_resumen=1)
            f_fecha_mod = meta_resumen.f_fecha_mod
            
            if f_fecha_mod:
                if not f_fecha_mod.tzinfo:
                    f_fecha_mod = make_aware(f_fecha_mod)
                
                meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }
                
                f_fecha_mod_formateada = f"{f_fecha_mod.day} de {meses[f_fecha_mod.month]} de {f_fecha_mod.year} a las {f_fecha_mod.strftime('%H:%M')} hrs."
            else:
                f_fecha_mod_formateada = "Fecha no disponible"
        except mae_est_meta_resumenes.DoesNotExist:
            f_fecha_mod_formateada = "Fecha no disponible"
        
        # Información de navegación según permisos
        menu_items = []
        if user_data['is_admin']:
            menu_items = [
                {'nombre': 'Estadística', 'url': '/est/Estadistica/', 'icono': 'grafico_n.png'},
                {'nombre': 'Logística', 'url': '/est/Logistica/', 'icono': 'logistica_gris.png'},
                {'nombre': 'Presupuesto', 'url': '/est/Presupuesto/', 'icono': 'presupuesto_gris.png'},
                {'nombre': 'Depósitos', 'url': '/est/Depositos/', 'icono': 'deposito_gris.png'},
                {'nombre': 'Cámaras', 'url': 'C:\\Program Files (x86)\\iVMS-4200 Site\\iVMS-4200 Client\\Server>iVMS-4200.Framework.S.exe', 'icono': 'camara_black.png'},
                {'nombre': 'Sinoe', 'url': '/est/PowerBi/Sinoe', 'icono': 'notificacion_gris.png'}
            ]
        
        # Respuesta completa
        response_data = {
            'usuario': user_data,
            'estadisticas_generales': estadisticas_generales,
            'juez_data': juez_data,
            'fecha_ultima_actualizacion': f_fecha_mod_formateada,
            'fecha_consulta': timezone.now().isoformat(),
            'menu_items': menu_items,
            'permisos': {
                'puede_ver_estadisticas': user.has_perm('est.list_mae_est_modulos'),
                'puede_ver_juez': user.has_perm('est.list_mae_est_jueces'),
                'puede_ver_organo': user.has_perm('est.list_mae_est_organo_jurisdiccionales')
            }
        }
        
        return JsonResponse(response_data, safe=False)

#Antonio cierre
