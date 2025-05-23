from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic
from django.contrib.auth import logout
from django.http import HttpResponse, Http404, JsonResponse                             #JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin      
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView                                #PasswordChangeView
from django.contrib.auth.hashers import make_password                                   #make_password
from django.db.models import Q                                                          #Modelo Q
from django.urls import reverse_lazy, reverse                                           #reverse_lazy
from django.contrib import messages                                                     #Message
from django.contrib.auth.decorators import login_required                               #LoginRequired
from datetime import datetime                                                           #Datetime
from django.views.generic import View
from django.utils.timezone import now
from django.db.models import Sum
from datetime import datetime, timedelta     
from collections import defaultdict
import locale
from django.db.models import Count
from calendar import month_name
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.template.loader import get_template

#? ===============================================
#? ================== MODELOS ====================
from django.contrib.auth.models import User, Group, Permission
from django.utils.timezone import now, timedelta
from bases.models import usuario, mae_est_sexos, hst_usuario_accesos
from est.models import mov_est_instancia_usuarios, mae_est_modulos, mae_est_meta_resumenes, mae_est_instancia, mae_est_organo_jurisdiccionales, mae_est_jueces, mov_est_instancia_jueces, mov_est_modulo_usuarios

#? ===============================================
#? =============== FORMULARIOS ===================
from .forms import UsuarioForm, PasswordChangeForm, UsuarioPassForm, UsuarioEditForm

class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = "bases/home.html"
    login_url = '/login'

    #Sobrescribe el método para agregar datos al contexto que será pasado a la plantilla.
    def get_context_data(self, **kwargs):
        #Llama al método de la clase base para inicializar el contexto.
        context = super().get_context_data(**kwargs)
        # Obtener el usuario actual
        user = self.request.user  
        # Contar los jueces con l_estado = 'S'
        context['cantidad_jueces_activos'] = mae_est_jueces.objects.filter(l_activo='S').count()
        context['cantidad_instancias'] = mae_est_instancia.objects.filter(l_ind_baja='N').count()
        #Filtra el modelo para verificar si el usuario está registrado como un juez activo.
        juez = mae_est_jueces.objects.filter(usuario=user, l_activo='S').first()

        #Comprueba si el usuario es un juez activo.
        if juez:
            # Obtener las instancias asignadas al juez
            instancias_asignadas = mov_est_instancia_jueces.objects.filter(
                n_id_juez=juez, l_activo='S'
            ).select_related('n_instancia')

            # Agrega las instancias asignadas al contexto, estructurándolas en una lista de diccionarios.
            context['instancias_asignadas'] = [
                {
                    'id': instancia.n_instancia.n_instancia_id,
                    'nombre': instancia.n_instancia.x_nom_instancia,
                }
                for instancia in instancias_asignadas
            ]

            # Calcula la fecha actual y el día anterior.
            fecha_actual = now()
            fecha_ayer = fecha_actual - timedelta(days=1)

            # Filtra los registros de mae_est_meta_resumenes correspondientes a las instancias del juez y al mes/año del día anterior.
            resumenes = mae_est_meta_resumenes.objects.filter(
                n_instancia__in=[instancia.n_instancia for instancia in instancias_asignadas],
                n_anio_est=fecha_ayer.year,
                n_mes_est=fecha_ayer.month
            ).select_related('n_instancia')

            # Estructura los datos de los resúmenes en una lista de diccionarios para el contexto.
            context['resumenes'] = [
                {
                    'id': resumen.n_id_meta_resumen,
                    'instancia': resumen.n_instancia.x_nom_instancia,
                    'anio': resumen.n_anio_est,
                    'mes': resumen.n_mes_est,
                    'produccion': resumen.m_estandar_prod,
                    'ideal_meta': resumen.m_ideal_avan_meta,
                    'situacion_carga':resumen.x_situacion_carga,
                    'nivel_produc' : resumen.x_niv_produc,
                    'ingresos' : resumen.m_t_ingreso,
                    'resueltos' : resumen.m_t_resuelto,
                    'IER': round((resumen.m_t_resuelto / resumen.m_t_ingreso) * 100, 2) if resumen.m_t_ingreso > 0 else 0,
                    'm_avance_meta' : resumen.m_avan_meta,
                }
                for resumen in resumenes
            ]

            #Calcula el avance de la meta y el ideal de la meta con valores predeterminados si no hay resúmenes.
            context['avance_meta'] = resumenes.first().m_avan_meta if resumenes else 0
            context['ideal_meta'] = resumenes.first().m_ideal_avan_meta if resumenes else 0
        
        #Asigna valores vacíos o predeterminados al contexto si el usuario no es juez activo.
        else:
            context['instancias_asignadas'] = []
            context['resumenes'] = []
            context['avance_meta'] = 0 
            
        #Captura la fecha y hora actuales.
        fecha_hora_actual = now()

        # Recupera un registro específico de mae_est_meta_resumenes, formatea su fecha de modificación, y maneja casos en los que no exista.
        #! (Debido a que la tabla de resumenes se resetea todo y se pone una misma fecha para todo, se elige el id 1)
        try:
            meta_resumen = mae_est_meta_resumenes.objects.get(n_id_meta_resumen=1)  
            f_fecha_mod = meta_resumen.f_fecha_mod

            if f_fecha_mod:
                # Si no tiene zona horaria, la hacemos consciente
                if not f_fecha_mod.tzinfo:
                    from django.utils.timezone import make_aware
                    f_fecha_mod = make_aware(f_fecha_mod)

                meses = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }

                # Formatear la fecha
                f_fecha_mod = f"{f_fecha_mod.day} de {meses[f_fecha_mod.month]} de {f_fecha_mod.year} a las {f_fecha_mod.strftime('%H:%M')} hrs."
            else:
                f_fecha_mod = "Fecha no disponible"
        except mae_est_meta_resumenes.DoesNotExist:
            f_fecha_mod = "Fecha no disponible"

        # Agrega la fecha y hora actuales, así como la fecha de modificación, al contexto.
        context['fecha_hora_actual'] = fecha_hora_actual
        context['f_fecha_mod'] = f_fecha_mod  # Agregar la fecha de modificación al contexto

        # Devuelve el contexto completo para que se use en la plantilla.
        return context

def custom_logout_view(request):
    logout(request)
    return redirect ('bases:login')

#!========================================================
#!===================== USUARIOS =========================
#!========================================================
#? ========================================================
#? Para Organos Jurisdiccionales
def Estadistica_por_organo(request):
    # Obtener todas las instancias
    instancias = mae_est_instancia.objects.filter(l_ind_baja='N')

    context = {
        "instancias": instancias,
    }
    return render(request, 'bases/pre_estadistica_organo.html', context)

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
        )

        # Convertir los datos a una lista y calcular el IER
        datos_lista = list(datos)
        for dato in datos_lista:
            m_t_ingreso = dato['m_t_ingreso'] or 0  # Evitar división por cero
            m_t_resuelto = dato['m_t_resuelto'] or 0
            dato['IER'] = round((m_t_resuelto / m_t_ingreso * 100) if m_t_ingreso > 0 else 0, 2)


        # Retornar los datos como JSON
        return JsonResponse({"datos": list(datos)}, safe=False)

    return JsonResponse({"error": "Invalid request"}, status=400)

#? ========================================================
#? Para Compara Organos
def preestadistica_comparar_instancias(request):
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

    return render(request, 'bases/pre_estadistica_comparar.html', {
        'organos': organos,
        'resumen1': resumen1,
        'resumen2': resumen2,
        'instancia_1': instancia_1,
        'instancia_2': instancia_2,
    })

def get_instancias_por_organo(request):
    org_id = request.GET.get('org_id')
    instancias = mae_est_instancia.objects.filter(c_org_jurisd__c_org_jurisd=org_id, l_ind_baja='N')
    data = [{'id': i.n_instancia_id, 'nombre': i.x_nom_instancia} for i in instancias]
    return JsonResponse(data, safe=False)


def grafica_por_instancia(request, modulo_id):
    locale.setlocale(locale.LC_TIME, "es_PE.UTF-8")
    modulo = get_object_or_404(mae_est_modulos, pk=modulo_id)

    yesterday = datetime.now() - timedelta(days=1)
    year = yesterday.year
    previous_month = yesterday.month

    previous_month_name = month_name[previous_month]
    current_month_name = month_name[datetime.now().month]

    # Obtener los datos de las instancias con el campo de jurisdicción
    resumenes = mae_est_meta_resumenes.objects.filter(
        n_id_modulo=modulo,
        n_anio_est=year,
        n_mes_est=previous_month
    ).values(
        'n_instancia__x_corto',
        'n_instancia__x_nom_instancia',
        'n_instancia__c_org_jurisd__x_nom_org_jurisd',  # Nombre del órgano jurisdiccional
        'x_situacion_carga',
        'x_niv_produc',
        'm_avan_meta',
        'm_ideal_avan_meta',
        'm_meta_preliminar',
        'n_carg_procesal_ini',
        'f_fecha_mod',
    ).annotate(
        total_ingreso=Sum('m_t_ingreso'),
        total_resuelto=Sum('m_t_resuelto')
    ).order_by('n_instancia__c_org_jurisd', '-m_avan_meta')

    # Agrupar por órgano jurisdiccional
    agrupados = defaultdict(list)
    for resumen in resumenes:
        # Convierte los valores Decimal a string
        resumen['m_avan_meta'] = float(resumen['m_avan_meta']) if resumen['m_avan_meta'] is not None else 0
        resumen['m_ideal_avan_meta'] = float(resumen['m_ideal_avan_meta']) if resumen['m_ideal_avan_meta'] is not None else 0

        agrupados[resumen['n_instancia__c_org_jurisd__x_nom_org_jurisd']].append(resumen)

    context = {
        "modulo": modulo,
        "agrupados": dict(agrupados),  # Convertir defaultdict a diccionario normal
        "mes_anterior": previous_month_name,
        "mes_actual": current_month_name,
        "anio_actual": year,
    }
    return render(request, 'bases/presidencia_gra_instancia.html', context)

def power_estadistica(request):
    return render(request,"bases/powerbi_estadistica.html")

def Sinoe(request):
    return render(request,"bases/sinoe.html")

def Jornada(request):
    return render(request,"bases/powerbi_jornada.html")

def Nepena(request):
    return render(request,"bases/powerbi_nepena.html")

#!========================================================
#!===================== USUARIOS =========================
#!========================================================
class UserView(LoginRequiredMixin,generic.ListView):
    model = usuario
    template_name = "bases/user_listar.html"
    context_object_name = 'obj'
    login_url = 'bases:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Contar la cantidad de usuarios con sexo MASCULINO (id=1)
        count_masculino = usuario.objects.filter(n_id_sexo__n_id_sexo=1).count()
        
        # Contar la cantidad de usuarios con sexo FEMENINO (id=2)
        count_femenino = usuario.objects.filter(n_id_sexo__n_id_sexo=2).count()

        # Añadir estas cantidades al contexto
        context['count_masculino'] = count_masculino
        context['count_femenino'] = count_femenino
        return context
    
def UserNew(request,pk=None):
    template_name = "bases/user_form.html"
    #Inicializa las variables context (para enviar datos a la plantilla), 
    #form (el formulario a usar), y obj (el usuario a editar, si corresponde).
    context = {}
    form = None
    obj =None
    
    #Verifica si la solicitud es de tipo GET, lo que indica que se quiere mostrar el formulario.
    if request.method =="GET":
        #Si no se proporciona un pk, significa que se está creando un nuevo usuario. 
        #Se inicializa el formulario sin datos previos.
        if not pk:
            form = UsuarioForm(instance = None)
        #Si se proporciona un pk, busca el usuario en la base de datos y lo asigna a obj.
        else:
            obj = usuario.objects.filter(id=pk).first()
            #Crea un formulario basado en los datos del usuario existente (obj) para edición.
            form = UsuarioEditForm(instance=obj)
        #Agrega el formulario y el usuario (si existe) al contexto para enviarlos a la plantilla.
        context["form"]= form
        context["obj"]= obj
        
        #Inicializa variables para los grupos del usuario y otros grupos disponibles.
        grupos_usuarios = None
        grupos = None
        #Si el usuario existe, obtiene todos los grupos a los que pertenece.
        if obj:
            grupos_usuarios = obj.groups.all()
            #Obtiene los grupos que no están asociados al usuario actual.
            grupos = Group.objects.filter(~Q(id__in=obj.groups.values('id')))
        #Añade estos grupos al contexto para su uso en la plantilla.
        context["grupos_usuario"]=grupos_usuarios
        context["grupos"]=grupos
    
    #Verifica si la solicitud es de tipo POST, lo que indica que se están enviando datos para procesar.
    if request.method == "POST":
        #Recupera los datos enviados en el formulario.
        data = request.POST
        # Para manejar archivos adjuntos como imágenes.
        files = request.FILES  
        #Extrae cada uno de los valores enviados desde el formulario.
        e = data.get("email")
        dni = data.get("x_dni")
        apellido_paterno = data.get("x_app_paterno")
        apellido_materno = data.get("x_app_materno")
        nombres = data.get("x_nombres")
        sexo_id = data.get("n_id_sexo")
        passw = data.get("password")
        name = data.get("username")
        imagen = request.FILES.get('profile_image') or 'img_perfil/perfil.png'
        
        #Busca el objeto sexo en la base de datos basado en el valor del campo sexo_id
        sexo = mae_est_sexos.objects.filter(n_id_sexo=sexo_id).first() if sexo_id else None

        #Si se proporciona un pk, intenta obtener el usuario existente.
        if pk:
            obj = usuario.objects.filter(id=pk).first()
            #Si el usuario no existe, imprime un mensaje de error 
            #(aunque debería manejarse mejor con un error explícito).
            if not obj:
                print("Error")
            #Si el usuario existe, actualiza sus campos con los datos proporcionados
            #y guarda los cambios en la base de datos. La contraseña se cifra con make_password.
            else:
                obj.email = e
                obj.username = name
                obj.x_dni = dni
                obj.x_app_paterno = apellido_paterno
                obj.x_app_materno = apellido_materno
                obj.x_nombres = nombres
                obj.n_id_sexo = sexo
                if imagen:  # Solo actualiza la imagen si se proporciona.
                    obj.profile_image = imagen
                # Cifra y actualiza la contraseña solo si se proporciona una nueva
                if passw:
                    obj.password = make_password(passw)

                obj.save()
        #Si no se proporciona un pk, crea un nuevo usuario con los datos proporcionados.
        else:
            obj = usuario.objects.create_user(
                email = e,
                username = name,
                password = passw,
                x_dni = dni,
                x_app_paterno = apellido_paterno,
                x_app_materno =  apellido_materno,
                x_nombres =  nombres,
                n_id_sexo = sexo,
                profile_image=imagen  # Asegúrate de pasar la imagen aquí.
            )
            #Imprime el correo y contraseña (aunque esto podría ser un problema de seguridad).
            print (obj.email,obj.password)
        #Redirige al usuario a la vista de lista después de procesar los datos.
        return redirect("bases:user_list")
        
    #Renderiza la plantilla con los datos del contexto si la solicitud es de tipo GET o no se ha hecho una redirección.   
    return render(request,template_name,context)

def UserPassEdit(request, pk):
    # Obtén al usuario o muestra un error 404
    user = get_object_or_404(usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioPassForm(request.POST)
        if form.is_valid():
            # Establece la nueva contraseña
            new_password = form.cleaned_data['new_password1']
            user.set_password(new_password)
            user.save()
            # Mensaje de éxito
            messages.success(request, f"La contraseña del usuario {user.username} se actualizó correctamente.")
            return redirect('bases:user_list')  # Cambia 'users_table' por el nombre de tu vista que lista usuarios
    else:
        form = UsuarioPassForm()

    return render(request, 'bases/user_pass_edit.html', {'form': form, 'user': user})

def group_user(request,id_usr,id_group):
    if request.method == "POST":
        #Para saber con que grupo trabajaremos
        usr = usuario.objects.filter(id=id_usr).first()
        #Si no existe ese grupo
        if not usr:
            messages.error(request,"Usuario no Existe")
            return HttpResponse("Usuario no Existe")
        #Capturemos la acción (ADD:Agregar | DEL:Eliminar)
        accion = request.POST.get("accion")
        grp = Group.objects.filter(id=id_group).first()
        #Si no existe el permiso
        if not grp:
            messages.error(request,"Grupo no Existe")
            return HttpResponse("Grupo no Existe")
        
        #Si la accion es igual a ADD
        if accion == "ADD":
            usr.groups.add(grp)
            return JsonResponse({"status": "success", "title": "Usuario Asignado a un Grupo"})
        elif accion == "DEL":
            usr.groups.remove(grp)
            return JsonResponse({"status": "success", "title": "Usuario Eliminado"})
        else:
            return JsonResponse({"status": "error", "title": "Acción no reconocida"}, status=400)
    return Http404("Método No Reconocido")

class UserDeleteView(View):
    def post(self, request, pk):
        try:
            user = get_object_or_404(usuario, pk=pk)
            user.is_active = False
            user.save()
            return JsonResponse({'success': True, 'message': f'Usuario {user.username} inactivado exitosamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
        
class UserActivarView(View):
    def post(self, request, pk):
        try:
            user = get_object_or_404(usuario, pk=pk)
            user.is_active = True
            user.save()
            return JsonResponse({'success': True, 'message': f'Usuario {user.username} Activado exitosamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

# Clase basada en vistas para asignar módulos a un usuario
class UserAssignModulesView(View):
    def get(self, request, pk):
        user = get_object_or_404(usuario, pk=pk)  # Obtiene el usuario
        modulos = mae_est_modulos.objects.filter(l_activo='S')  # Obtiene los módulos activos
        assigned_modulos = mov_est_modulo_usuarios.objects.filter(usuario=user).values_list('n_id_modulo', flat=True)  # Obtiene los módulos asignados al usuario

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('bases/user_modulos.html', {
                'user': user,
                'modulos': modulos,
                'assigned_modulos': assigned_modulos,
            }, request)
            return JsonResponse({'html': html})

        return render(request, 'bases/user_modulos.html', {
            'user': user,
            'modulos': modulos,
            'assigned_modulos': assigned_modulos,
        })

    def post(self, request, pk):
        user = get_object_or_404(usuario, pk=pk)  # Obtiene el usuario con el ID proporcionado
        selected_modulos = request.POST.getlist('modulos')  # Obtiene la lista de IDs de los módulos seleccionados

        # Elimina todas las asignaciones previas de módulos para este usuario
        mov_est_modulo_usuarios.objects.filter(usuario=user).delete()

        # Crea nuevas asignaciones para cada módulo seleccionado
        for modulo_id in selected_modulos:
            # Obtén el módulo y crea la asignación
            modulo = get_object_or_404(mae_est_modulos, n_id_modulo=modulo_id)
            mov_est_modulo_usuarios.objects.create(usuario=user, n_id_modulo=modulo)

        # Devuelve una respuesta JSON de éxito
        return JsonResponse({'success': True, 'message': 'Módulos asignados exitosamente.'})

#!========================================================
#!=========== GENERAR PDF PARA CREDENCIAL ================
#!========================================================
def generar_credenciales_pdf(request, user_id):
    # Obtener el usuario
    user = get_object_or_404(usuario, id=user_id)
    
    # Datos para el PDF
    context = {
        'username': user.username,
        'password': 'pj123456',
        'nombres': user.x_nombres,
        'apellidos': f"{user.x_app_paterno} {user.x_app_materno}",
        'dni': user.x_dni,
        'telefono': user.x_telefono,
        'email': user.email,
    }
    
    # Generar el PDF
    template = get_template('bases/credenciales_pdf.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="credenciales_{user.username}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Verificar si hubo errores al generar el PDF
    if pisa_status.err:
        return HttpResponse("Ocurrió un error al generar el PDF", content_type='text/plain')
    return response

#!========================================================
#!================ CAMBIAR CONTRASEÑA ====================
#!========================================================
class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = PasswordChangeForm  # Utiliza el formulario personalizado
    template_name = 'bases/cambiar_password.html'  # El template donde se mostrará el formulario
    success_url = reverse_lazy('bases:home')  # Redirige después de cambiar la contraseña

    def form_valid(self, form):
        # Puedes agregar lógica adicional aquí si es necesario
        messages.success(self.request, "Su contraseña ha sido cambiada con éxito.")
        return super().form_valid(form)

#!========================================================
#!===================== GRUPOS ==========================
#!========================================================
class GroupView(LoginRequiredMixin,generic.ListView):
    model = Group
    template_name = "bases/group_listar.html"
    context_object_name = 'obj'
    login_url = 'bases:login'

@login_required(login_url='bases:login')
def user_group_admin(request,pk=None):
    template_name= "bases/detalles_grupo.html"
    context = {}
    
    obj = Group.objects.filter(id=pk).first()
    context["obj"] = obj
    permisos = {}
    permisos_grupo = {}
    context['permisos']=permisos
    context['permisos_grupo']=permisos_grupo
    
    if obj:
        #Obtener todos los permisos
        permisos_grupo = obj.permissions.all()
        context['permisos_grupo']=permisos_grupo
        
        #Filtraremos todos los permisos disponibles, excluyendo los que ya tiene asignado el grupo
        permisos = Permission.objects.filter(~Q(group=obj))
        context['permisos']=permisos
    
    if request.method == "POST":
        name = request.POST.get("name")
        grp = Group.objects.filter(name=name).first()
        if grp and grp.id != pk:
            print ("Grupo ya existe")
            return redirect("bases:group_new")
        #Si el grupo no existe pero el pk no existe | Entonces es nuevo
        if not grp and pk != None:
            grp = Group.objects.filter(id=pk).first()
            grp.name = name
            grp.save()
        elif not grp and pk == None:
            grp = Group(name = name)  
        else:
            ...  
        grp.save()
        return redirect("bases:group_edit", grp.id)    
    return render(request,template_name,context) 

def group_delete(request,pk):
    if request.method == "POST":
        grp = Group.objects.filter(id=pk).first()
        
        if not grp:
            print("Grupo no Existe")
        else:
            grp.delete()
        return HttpResponse("OK")
    
def group_permiso(request,id_grp,id_perm):
    if request.method == "POST":
        #Para saber con que grupo trabajaremos
        grp = Group.objects.filter(id=id_grp).first()
        #Si no existe ese grupo
        if not grp:
            messages.error(request,"Grupo no Existe")
            return HttpResponse("Grupo no Existe")
        #Capturemos la acción (ADD:Agregar | DEL:Eliminar)
        accion = request.POST.get("accion")
        perm = Permission.objects.filter(id=id_perm).first()
        #Si no existe el permiso
        if not perm:
            messages.error(request,"Permiso no Existe")
            return HttpResponse("Permiso no Existe")
        
        #Si la accion es igual a ADD
        if accion == "ADD":
            grp.permissions.add(perm)
            return JsonResponse({"status": "success", "title": "Permiso Agregado"})
        elif accion == "DEL":
            grp.permissions.remove(perm)
            return JsonResponse({"status": "success", "title": "Permiso Eliminado"})
        else:
            return JsonResponse({"status": "error", "title": "Acción no reconocida"}, status=400)
    return Http404("Método No Reconocido")


#! =======================================================

#! =======================================================
def listar_accesos(request):
    # Consulta para listar accesos
    accesos = hst_usuario_accesos.objects.select_related('usuario').all().order_by('-f_fecha_hora')

    # Consulta para contar ingresos por usuario
    ingresos = (
        hst_usuario_accesos.objects.values('usuario__x_nombres', 'usuario__x_app_paterno')
        .annotate(total_ingresos=Count('id'))
        .order_by('-total_ingresos')  # Ordenar de mayor a menor número de ingresos
    )

    # Renderizar ambos contextos en la misma plantilla
    return render(request, 'bases/listar_accesos.html', {'accesos': accesos, 'ingresos': ingresos})