from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from est import views
#Antonio inicio
from est.views import JuecesListView , JuecesCreateView, JuecesDeleteView, JuecesEditarView, JuecesActivarView,\
                    JuecesInstanciaListView, JuecesInstanciaCreateView, JuecesInstanciaDeleteView, \
                    NivelProductividad,\
                    ModuloListView, ModuloCreateView, ModuloUpdateView, ModuloDeleteView, \
                    EscalaListView, ListarEstProdView, InstanciasListView, Estadistica_mensual,\
                    obtener_datos_instancia, InstanciaModulosListar,\
                    ConfiguracionMetas, meta_conf_seed_view, MetaResumenListView, MetaCuadroMensualView, MetaCuadroMensualJSONView, LoginAPIView, MetaCuadroMensualJSONPublicView, HomeDashboardJSONView,\
                    MetaResumenOpcionBListView, crear_snapshot_temporal, MetaResumenGuardarBulk, meta_resumen_cerrar_definitivo, meta_resumen_volver_abrir
#agreguee LoginAPIView, MetaCuadroMensualJSONPublicView, HomeDashboardJSONView,
#Antonio cierre

urlpatterns = [
    #? =========================================================
    #? ====================== JUECES ===========================
    path('Jueces/', JuecesListView.as_view(), name='jueces_list'),
    path('Jueces/Crear/', JuecesCreateView.as_view(), name='jueces_crear'),
    path('Jueces/Eliminar/<int:pk>/', JuecesDeleteView.as_view(), name='jueces_eliminar'),
    path('Jueces/Editar/<int:pk>/', JuecesEditarView.as_view(), name='jueces_editar'),
    path('Jueces/Activar/<int:pk>/', JuecesActivarView.as_view(), name='jueces_activar'),

    #? =========================================================
    #? ================== JUECES INSTANCIAS ====================
    path('JuezInstancia/', JuecesInstanciaListView.as_view(), name='juez_instancia_list'),
    path('JuezInstancia/Crear/', JuecesInstanciaCreateView.as_view(), name='juez_instancia_crear'),
    path('JuezInstancia/Eliminar/<int:pk>/', JuecesInstanciaDeleteView.as_view(), name='juez_instancia_eliminar'),

    #? =========================================================
    #? =======================INSTANCIAS =======================
    path('Instancias/', InstanciasListView.as_view(), name='instancia_list'),

    #? =========================================================
    #? ================ ESTANDAR DE PRODUCCIÓN =================
    path('EstandarProduccion/', ListarEstProdView.as_view(), name='estandar_prod_list'),  # Lista de módulos

    #? =========================================================
    #? ======================== MÓDULOS ========================
    path('Modulos/', ModuloListView.as_view(), name='modulo_list'),  # Lista de módulos
    path('Modulos/Instancia/<int:modulo_id>/', InstanciaModulosListar, name='modulo_instancia_list'),  # Lista de módulos
    path('Modulo/create/', ModuloCreateView.as_view(), name='modulo_create'),  # Crear módulo
    path('Modulo/update/<int:pk>/', ModuloUpdateView.as_view(), name='modulo_update'),  # Actualizar módulo
    path('Modulo/delete/<int:pk>/', ModuloDeleteView.as_view(), name='modulo_delete'),  # Eliminar módulo
    path('Modulo/activar/<int:pk>/', views.ModuloActivarView.as_view(), name='modulo_activar'),  # Activar módulo

    #? =========================================================
    #? ======================== ESCALAS ========================
    path('Escalas/',EscalaListView.as_view(),name='escala_list'),
    path('Escala/<int:escala_id>/Detalle', views.agregar_detalle_escala, name='agregar_detalle_escala'),
    path('Escalas/<int:pk>/data/', views.get_escala_data, name='escala_edit'),
    path("metas/cuadro-anual/", MetaCuadroMensualView.as_view(), name="metas_cuadro_mensual"),
    path("metas/cuadro-anual/json/", MetaCuadroMensualJSONView.as_view(), name="metas_cuadro_mensual_json"),
    path("metas/cuadro-anual/api/", MetaCuadroMensualJSONPublicView.as_view(), name="metas_cuadro_mensual_api"),
    path("api/login/", LoginAPIView.as_view(), name="api_login"),
    #Antonio inicio
    path("api/dashboard/", HomeDashboardJSONView.as_view(), name="api_dashboard"),
    
    #? =========================================================
    #? =============== CONFIGURACION DE METAS ==================
    path("configuracion-metas/", ConfiguracionMetas.as_view(), name="configuracion_metas_list"),
    path("configuracion-metas/seed/", meta_conf_seed_view, name="meta_conf_seed"),

    path("meta-resumen/<int:pk>/modificar/", views.meta_resumen_guardar_modificado, name="meta_resumen_guardar_modificado"),
    path("meta-resumen/modificar/bulk/", views.meta_resumen_guardar_bulk, name="meta_resumen_guardar_bulk"),

    path('meta-b/', MetaResumenOpcionBListView.as_view(), name='meta_resumen_b_list'),
    path('meta-b/crear-snapshot/', crear_snapshot_temporal, name='crear_snapshot_temporal'),
    path('meta-b/guardar-bulk/', MetaResumenGuardarBulk.as_view(), name='meta_resumen_guardar_bulk'),
    path('meta-b/cerrar-definitivo/', meta_resumen_cerrar_definitivo, name='meta_resumen_cerrar_definitivo'),
    path('meta-b/volver-abrir/', meta_resumen_volver_abrir, name='meta_resumen_volver_abrir'),
    
    #? =========================================================
    #? =============== CONFIGURACION DE METAS ==================
    path("metas-resumen/", MetaResumenListView.as_view(), name="metas_resumen_list"),

    #? =========================================================
    #? ======================== GRAFICOS ========================
    path('Estadistica/', views.Estadistica, name="estadistica_menu"),
    path('Estadistica/PorModulos/', views.Estadistica_por_modulo, name="estadistica_modulo"),
    path('Estadistica/DescripcionModulos/<int:modulo_id>/', views.Estadistica_descripcion, name="descripcion_modulo"),
    path('Estadistica/Mensual/<int:modulo_id>/', views.Estadistica_mensual, name="estadistica_mensual"),
    path('Estadistica/PorModulos/<int:modulo_id>/ActualVsCerrado/', views.Estadistica_actual_cerrado, name="estadistica_actual_cerrado"),

    path('Estadistica/PorModulos/<int:modulo_id>/Grafica/', views.Estadistica_modulo_grafica, name="estadistica_modulo_grafica"),
    path('Estadistica/OrganoJurisdiccional/', views.Estadistica_por_organo, name="estadistica_organo"),
    path('Estadistica/OrganoJurisdiccional/datos/', views.obtener_datos_instancia, name='obtener_datos_instancia'),

    path('Estadistica/CompararInstancias', views.comparar_instancias, name='comparar_instancias'),
    path('get_instancias/', views.get_instancias_por_organo, name='get_instancias_por_organo'),
    #? =========================================================
    #? ======================== ESCALAS ========================
    path('NivelProductividad/', views.NivelProductividad, name='nivel_productividad'),

    #? =========================================================
    #? ======================== ESCALAS ========================
    path('PowerBi/DashboardEstadistica', views.PowerEstadistica, name="power_estadistica"),
    path('PowerBi/Sinoe', views.PowerSinoe, name="power_sinoe"),
    path('PowerBi/JornadaExtraordinaria', views.PowerJornada, name="power_jornada"),
    path('PowerBi/JuzgadoNepena', views.PowerNepena, name="power_nepena"),

    #? =========================================================
    #? ====================== LOGISTICA ========================
    #? =========================================================
    path('Logistica/', views.Logistica_menu, name="logistica_menu"),

    #? =========================================================
    #? ===================== PRESUPUESTO =======================
    #? =========================================================
    path('Presupuesto/', views.Presupuesto_menu, name="presupuesto_menu"),

    #? =========================================================
    #? ====================== DEPOSITO =========================
    #? =========================================================
    path('Depositos/', views.Depositos_menu, name="depositos_menu"),

    #? =========================================================
    #? ======================= CÁMARAS =========================
    #? =========================================================
    path('Camaras/', views.Camaras_menu, name="camaras_menu"),

    #? =========================================================
    #? ======================= CÁMARAS =========================
    #? =========================================================
    
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

