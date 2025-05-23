from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import datetime, timedelta                                                      
from django.db.models import Sum
from django.utils.timezone import now, localtime
from datetime import timedelta
from collections import defaultdict
from calendar import month_name
from decimal import Decimal
from django.db.models import OuterRef, Subquery, Q, Value, CharField
from django.db.models.functions import Concat
from django.contrib.auth.decorators import login_required
import locale
from django.utils import timezone

from .forms import ModuloForm, AsignacionJuezForm, EstProdAnualForm, JuezForm
from bases.models import usuario
from .models import mae_est_jueces , mae_est_juez_tipos, mae_est_modulos, mae_est_escalas,\
                    mov_est_instancia_jueces, \
                    mov_est_instancia_usuarios, mov_est_estprod_anuales,\
                    mae_est_instancia, mae_est_meta_resumenes, mae_est_organo_jurisdiccionales, mae_est_escala_detalle,\
                    mov_est_instancia_modulos, mae_est_meta_detalles, mov_est_modulo_usuarios


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

#!========================================================
#!================ MODULOS - INSTANCIAS===================
#!========================================================
@login_required
def InstanciaModulosListView(request, modulo_id):
    # Obtén el módulo seleccionado
    modulo = get_object_or_404(mae_est_modulos, n_id_modulo=modulo_id)
    
    # Filtra las instancias asociadas al módulo en la tabla mov_est_instancia_modulos
    instancias_modulos = mov_est_instancia_modulos.objects.filter(
        n_id_modulo=modulo
    ).select_related('n_instancia','n_instancia__c_org_jurisd')  # Optimiza el acceso a la relación n_instancia
    
    # Renderiza el template y envía las instancias y el módulo seleccionado
    return render(
        request,
        'est/instancia_modulos_list.html',
        {
            "modulo": modulo,
            "instancias_modulos": instancias_modulos,
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

#? ===========================================================================================
#? ========================= TABLERO DE CONTROL DE PRESIDENCIA ===============================
#? ===========================================================================================
#!========================================================
#!================== ESTADISTICA =========================
#!========================================================   
@login_required
def Estadistica(request):
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

    # Renderizar la plantilla con los módulos asignados
    return render(request, "est/estadistica_modulos.html", {'dato': modulos_asignados})

#!========================================================
#!====== ESTADISTICA POR MODULO MOSTRANDO GRAFICO ========
#!========================================================   
@login_required
def Estadistica_modulo_grafica(request, modulo_id):
    # Configura el idioma local para formatear nombres de meses en español
    try:
        # Cambia a tu configuración regional
        locale.setlocale(locale.LC_ALL, 'es_PE.UTF-8')  # Cambia a tu configuración regional
    except locale.Error as e:
        # Captura cualquier error al configurar el locale y lo imprime
        print(f"Error al configurar el locale: {e}")
    # Obtiene el módulo correspondiente al `modulo_id` o lanza un error 404 si no existe
    modulo = get_object_or_404(mae_est_modulos, pk=modulo_id)

    # Calcula la fecha del día anterior y extrae el año y el mes correspondiente
    yesterday = datetime.now() - timedelta(days=1)
    year = yesterday.year
    previous_month = yesterday.month

    # Obtiene los nombres del mes actual y del mes anterior usando `month_name`
    previous_month_name = month_name[previous_month]
    current_month_name = month_name[datetime.now().month]

    # Subquery para obtener el nombre completo concatenado del juez activo asignado a una instancia
    juez_subquery = mov_est_instancia_jueces.objects.filter(
        n_instancia=OuterRef('n_instancia__pk'),
        l_activo='S'
    ).order_by('-f_fecha_creacion').values(
        'n_id_juez__usuario__x_nombres'
    )[:1]

    # Si quieres concatenar nombre + apellido paterno + materno:
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

    # Consulta los datos de las instancias relacionadas con el módulo y agrega cálculos
    resumenes = mae_est_meta_resumenes.objects.filter(
        # Filtra por el módulo actual
        n_id_modulo=modulo,        
        # Filtra por el año calculado             
        n_anio_est=year,
        # Filtra por el mes anterior
        n_mes_est=previous_month
    ).values(
        'n_instancia__x_corto',
        'n_instancia__x_nom_instancia',
        'n_instancia__c_org_jurisd__x_nom_org_jurisd',  # Nombre del órgano jurisdiccional
        'f_fecha_mod',
        'x_situacion_carga',
        'x_niv_produc',
        'm_avan_meta',
        'm_ideal_avan_meta',
        'm_meta_preliminar',
        'n_carg_procesal_ini',
    ).annotate(
        # Calcula los totales de ingresos y resueltos
        total_ingreso=Sum('m_t_ingreso'),
        total_resuelto=Sum('m_t_resuelto'),

        # Agregamos info del juez con Subquery: concatenamos nombre completo
        juez_nombre=Subquery(juez_fullname_subquery)
    ).order_by('n_instancia__c_org_jurisd', '-m_avan_meta')

    # Intenta obtener la fecha de modificación de un registro específico
    try:
        fecha_modificacion = mae_est_meta_resumenes.objects.get(n_id_meta_resumen=1).f_fecha_mod
        # Diccionario para convertir el número del mes al nombre del mes en español
        meses = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
            5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
            9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }

        # Formatea la fecha al estilo "día de mes de año"
        fecha_modificacion_formateada = (
            f"{fecha_modificacion.day} de {meses[fecha_modificacion.month]} de {fecha_modificacion.year} a las {fecha_modificacion.strftime('%H:%M')} hrs."
        )
    except mae_est_meta_resumenes.DoesNotExist:
        # Si el registro no existe, establece una fecha predeterminada
        fecha_modificacion_formateada = "Sin fecha"

    # Agrupa los datos por el nombre del órgano jurisdiccional
    agrupados = defaultdict(list)
    for resumen in resumenes:
        # Convierte valores decimales a flotantes para evitar problemas de representación
        resumen['m_avan_meta'] = float(resumen['m_avan_meta']) if resumen['m_avan_meta'] is not None else 0
        resumen['m_ideal_avan_meta'] = float(resumen['m_ideal_avan_meta']) if resumen['m_ideal_avan_meta'] is not None else 0

        # Formatea la fecha de modificación si está disponible
        resumen['f_fecha_mod'] = resumen['f_fecha_mod'].strftime('%d/%m/%Y a las %H:%M') \
            if resumen['f_fecha_mod'] else 'Sin fecha'
        
        # Si no hay juez asignado, ponemos un valor por defecto
        resumen['juez_nombre'] = resumen.get('juez_nombre') or 'Sin juez asignado'

        # Agrega el resumen al grupo correspondiente por órgano jurisdiccional
        agrupados[resumen['n_instancia__c_org_jurisd__x_nom_org_jurisd']].append(resumen)

    # Prepara el contexto para pasar los datos al template
    context = {
        "modulo": modulo,
        "agrupados": dict(agrupados),  # Convertir defaultdict a diccionario normal
        "mes_anterior": previous_month_name,
        "mes_actual": current_month_name,
        "anio_actual": year,
        "fecha_modificacion": fecha_modificacion_formateada,  # Agregar la fecha al contexto
    }
    
    # Renderiza el template con el contexto preparado
    return render(request, 'est/estadistica_modulos_grafica.html', context)

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

        context['resumenes'] = [
            {
                'id': resumen.n_id_meta_resumen,
                'instancia': resumen.n_instancia.x_nom_instancia,
                'anio': resumen.n_anio_est,
                'mes': resumen.n_mes_est,
                'produccion': resumen.m_estandar_prod,
                'ideal_meta': resumen.m_ideal_avan_meta,  # Meta ideal individual
                'avance_meta': resumen.m_avan_meta,  # Avance meta individual
                'meta_preliminar': resumen.m_meta_preliminar,
                'carga_inicial': resumen.n_carg_procesal_ini,
                'situacion_carga': resumen.x_situacion_carga,
                'nivel_produc': resumen.x_niv_produc,
                'ingresos': resumen.m_t_ingreso,
                'resueltos': resumen.m_t_resuelto,
                'IER': round((resumen.m_t_resuelto / resumen.m_t_ingreso) * 100, 2) if resumen.m_t_ingreso > 0 else 0,
            }
            for resumen in resumenes
        ]
    else:
        context['resumen_por_instancia'] = {}
        context['resumenes'] = []

    # Fecha y hora actual
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

    # Renderizar el template con el contexto
    return render(request, template_name, context)

#! =======================================================
#! ==================== POWER BI =========================
#! ======================================================= 
@login_required
def PowerSinoe(request):
    return render(request,"est/powerbi_sinoe.html")  

@login_required
def PowerJornada(request):
    return render(request,"est/powerbi_jornada.html")  

@login_required
def PowerEstadistica(request):
    return render(request,"est/powerbi_estadistica.html")  

@login_required
def PowerNepena(request):
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