from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from est import views
from est.views import JuecesListView , JuecesCreateView, JuecesDeleteView, JuecesEditarView, JuecesActivarView,\
                    JuecesInstanciaListView, JuecesInstanciaCreateView, \
                    NivelProductividad,\
                    ModuloListView, ModuloCreateView, ModuloUpdateView, ModuloDeleteView, \
                    EscalaListView, ListarEstProdView, InstanciasListView,\
                    obtener_datos_instancia, InstanciaModulosListView


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

    #? =========================================================
    #? =======================INSTANCIAS =======================
    path('Instancias/', InstanciasListView.as_view(), name='instancia_list'),

    #? =========================================================
    #? ================ ESTANDAR DE PRODUCCIÓN =================
    path('EstandarProduccion/', ListarEstProdView.as_view(), name='estandar_prod_list'),  # Lista de módulos

    #? =========================================================
    #? ======================== MÓDULOS ========================
    path('Modulos/', ModuloListView.as_view(), name='modulo_list'),  # Lista de módulos
    path('Modulos/Instancia/<int:modulo_id>/', InstanciaModulosListView, name='modulo_instancia_list'),  # Lista de módulos
    path('Modulo/create/', ModuloCreateView.as_view(), name='modulo_create'),  # Crear módulo
    path('Modulo/update/<int:pk>/', ModuloUpdateView.as_view(), name='modulo_update'),  # Actualizar módulo
    path('Modulo/delete/<int:pk>/', ModuloDeleteView.as_view(), name='modulo_delete'),  # Eliminar módulo

    #? =========================================================
    #? ======================== ESCALAS ========================
    path('Escalas/',EscalaListView.as_view(),name='escala_list'),
    path('Escala/<int:escala_id>/Detalle', views.agregar_detalle_escala, name='agregar_detalle_escala'),
    path('Escalas/<int:pk>/data/', views.get_escala_data, name='escala_edit'),

    #? =========================================================
    #? ======================== ESCALAS ========================
    path('Estadistica/', views.Estadistica, name="estadistica_menu"),
    path('Estadistica/PorModulos/', views.Estadistica_por_modulo, name="estadistica_modulo"),
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
    
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

