from django.urls import path
from bases.views import Home
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from bases import views
from django.views.generic import TemplateView
#VISTAS
from bases.views import Home, UserView, GroupView,UserPasswordChangeView,\
                        UserNew, user_group_admin, custom_logout_view, group_delete, group_permiso, group_user, UserPassEdit, \
                        UserDeleteView, UserActivarView, UserAssignModulesView


urlpatterns = [
    path('',Home.as_view(),name='home'),
    path('login/',auth_views.LoginView.as_view(template_name="bases/login.html"),name='login'),
    path('logout/',custom_logout_view,name='logout'),

    path('usuario/delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),  # Eliminar Usuario
    path('usuario/activar/<int:pk>/', UserActivarView.as_view(), name='user_activar'),  # Activar Usuario
    path('user/<int:pk>/AsignarModulos/', UserAssignModulesView.as_view(), name='user_asignar_modulos'),
    path('usuarios/<int:user_id>/credenciales/', views.generar_credenciales_pdf, name='generar_credenciales_pdf'),

    path('Presidencia/estadistica/OrganoJurisdiccional/datos/', views.obtener_datos_instancia, name='obtener_datos_instancia'),
    path('Presidencia/estadistica/OrganoJurisdiccional/', views.Estadistica_por_organo, name="estadistica_organo"),

    path('Estadistica/CompararInstancias', views.preestadistica_comparar_instancias, name='comparar_instancias'),
    path('get_instancias/', views.get_instancias_por_organo, name='get_instancias_por_organo'),
    

    path('Presidencia/power/estadistica',views.power_estadistica,name='pre_power_estadistica'),
    path('Presidencia/sinoe/',views.Sinoe,name='pre_sinoe'),
    path('Presidencia/JornadaExtraordinaria/',views.Jornada,name='pre_power_jornada'),
    path('Presidencia/Nepena/',views.Nepena,name='pre_power_nepena'),    

    path('usuarios/',UserView.as_view(),name="user_list"),
    path('usuarios/nuevo',UserNew,name="user_new"),
    path('usuarios/editar/<int:pk>',UserNew,name="user_edit"),
    path('usuarios/cambiarpassword/<int:pk>',UserPassEdit,name="user_pass_edit"),
    
    path('grupos/',GroupView.as_view(),name="group_list"),
    path('grupos/add',user_group_admin,name="group_new"),
    path('grupos/editar/<int:pk>',user_group_admin,name="group_edit"),
    path('grupos/eliminar/<int:pk>',group_delete,name="group_delete"),
    
    path('grupos/permisos/<int:id_grp>/<int:id_perm>',group_permiso,name="grupo_permiso"),
    path('grupos/usuarios/<int:id_usr>/<int:id_group>',group_user,name="grupo_usuario"),
    
    path('cambiar-password/', UserPasswordChangeView.as_view(), name='cambiar_password'),
    # Puedes añadir una URL adicional para mostrar el mensaje de éxito:
    path('cambiar-password/hecho/', TemplateView.as_view(template_name='bases/password_change_done.html'), name='password_change_done'),   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
