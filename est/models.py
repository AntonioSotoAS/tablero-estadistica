from django.db import models
from django.contrib.auth.models import AbstractUser
from bases.models import mae_est_usuarios_groups, usuario, TablaControl, TablaAuditoria
from django.utils.translation import gettext_lazy as _

#! =====================================================================
#! TABLA MODULOS
#! =====================================================================
class mae_est_modulos(TablaControl):
    n_id_modulo = models.AutoField(primary_key=True)
    x_nombre = models.CharField(max_length=100)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_activo = models.CharField(max_length=1,default='S')

    class Meta:
        db_table = 'mae_est_modulos'
        permissions = [
            ("list_mae_est_modulos", _("Listar Módulos")),
        ]

    def __str__(self):
        return self.x_nombre

#! =====================================================================
#! TABLA ESCALAS
#! =====================================================================
class mae_est_escalas(TablaControl):
    n_id_escala = models.AutoField(primary_key=True)
    x_nombre = models.CharField(max_length=100)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    x_resolucion = models.CharField(max_length=255)
    x_anio = models.CharField(max_length=4)
    l_activo = models.CharField(max_length=1,default='S')

    class Meta:
        db_table = 'mae_est_escalas'
    def __str__(self):
        return self.x_nombre

#! =====================================================================
#! TABLA DETALL ESCALAS
#! =====================================================================
class mae_est_escala_detalle(TablaControl):
    n_id_escala_detalle = models.AutoField(primary_key=True)
    n_id_escala = models.ForeignKey(mae_est_escalas,on_delete=models.PROTECT)
    x_mes = models.CharField(max_length=2)
    m_porcentaje = models.DecimalField(max_digits=5,decimal_places=2)
    class Meta:
        db_table = 'mae_est_escala_detalle'

#! =====================================================================
#! TABLA ORGANO_JURISDICCIONAL
#! =====================================================================
class mae_est_organo_jurisdiccionales(TablaControl):
    c_org_jurisd = models.CharField(max_length=2,primary_key=True)
    x_nom_org_jurisd = models.CharField(max_length=30)
    x_nom_org_jurisd_corto = models.CharField(max_length=2)
    l_activo = models.CharField(max_length=1,default='S')
    class Meta:
        db_table = 'mae_est_organo_jurisdiccionales'
        permissions = [
            ("list_mae_est_organo_jurisdiccionales", _("Listar Organos Jurisdiccionales")),
        ]

#! =====================================================================
#! TABLA SEDES
#! =====================================================================
class mae_est_sedes(TablaControl):
    c_sede = models.CharField(max_length=4,primary_key=True)
    x_desc_sede = models.CharField(max_length=60)
    l_activo = models.CharField(max_length=1,default='S')
    class Meta:
        db_table = 'mae_est_sedes'

#! =====================================================================
#! TABLA INSTANCIA
#! =====================================================================
class mae_est_instancia(TablaControl):
    c_distrito = models.CharField(max_length=3)
    c_provincia = models.CharField(max_length=4)
    c_instancia = models.CharField(max_length=3)
    c_org_jurisd = models.ForeignKey(mae_est_organo_jurisdiccionales,on_delete=models.PROTECT)
    c_sede = models.ForeignKey(mae_est_sedes,on_delete=models.PROTECT)
    n_instancia_id = models.IntegerField(primary_key=True)
    x_nom_instancia = models.CharField(max_length=60)
    n_instancia = models.IntegerField()
    n_modulo = models.IntegerField(null=True,blank = True)
    l_modulo_ejecucion = models.CharField(max_length=1)
    x_corto = models.CharField(max_length=4)
    l_ind_baja = models.CharField(max_length=1)
    class Meta:
        db_table = 'mae_est_instancia'
    def __str__(self):
        return self.x_nom_instancia

#! =====================================================================
#! TABLA INSTANCIA_USUARIOS
#! =====================================================================   
class mov_est_instancia_usuarios(TablaControl):
    n_id_instancia_usuario = models.AutoField(primary_key=True)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    usuario= models.ForeignKey(usuario,on_delete=models.PROTECT)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_activo = models.CharField(max_length=1,default='S')
    class Meta:
        db_table = 'mov_est_instancia_usuarios'

#! ====================================================================
#! TABLA INSTANCIA_ESCALAS
#! ====================================================================
class mov_est_instancia_escalas(TablaControl):
    n_id_instancia_escala = models.AutoField(primary_key=True)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    l_id_escala = models.ForeignKey(mae_est_escalas,on_delete=models.PROTECT)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_activo = models.CharField(max_length=1,default='S')
    class Meta:
        db_table = 'mov_est_instancia_escalas'

#! ====================================================================
#! TABLA MAE_EST_TIPO_ESP
#! ====================================================================
class mae_est_tipo_esp(TablaControl):
    n_id_tipo_esp = models.AutoField(primary_key=True)
    x_descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = 'mae_est_tipo_esp'

#! ====================================================================
#! TABLA ESTANDAR_PRODUCCION_ANULES
#! ====================================================================
class mov_est_estprod_anuales(TablaControl):
    n_id_instancia_factor = models.AutoField(primary_key=True)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    m_estandar_prod = models.IntegerField()
    m_carga_min = models.DecimalField(max_digits=5,decimal_places=2)
    m_carga_max = models.DecimalField(max_digits=5,decimal_places=2)
    m_meta_preliminar = models.DecimalField(max_digits=5,decimal_places=2)
    m_meta_final = models.DecimalField(max_digits=5,decimal_places=2)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_org_penal = models.CharField(max_length=1,default='S')
    l_unico_especialidad = models.CharField(max_length=1,default='S')
    l_volencia_familiar = models.CharField(max_length=1,default='S')
    c_zona = models.CharField(max_length=1)
    n_id_tipo_esp= models.ForeignKey(mae_est_tipo_esp,on_delete=models.PROTECT, null=True)
    l_activo = models.CharField(max_length=1,default='S')
    n_instancia_padre = models.IntegerField()

    class Meta:
        db_table = 'mae_est_instancia_factores'

#! ====================================================================
#! TABLA INSTANCIA_MODULOS
#! ====================================================================
class mov_est_instancia_modulos(TablaControl):
    n_id_instancia_modulo = models.AutoField(primary_key=True)
    n_id_modulo = models.ForeignKey(mae_est_modulos,on_delete=models.PROTECT)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_activo = models.CharField(max_length=1,default='S')
    n_orden = models.IntegerField()
    
    class Meta:
        db_table = 'mov_est_instancia_modulos'

#! ====================================================================
#! TABLA INSTANCIA_DETALLES
#! ====================================================================
class hst_est_instancia_detalles(TablaControl):
    n_id_instancia_detalle = models.AutoField(primary_key=True)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    x_resolucion = models.CharField(max_length=200)
    x_pdf_res = models.FileField(upload_to='instancia/')
    class Meta:
        db_table = 'hst_est_instancia_detalles'

class mae_est_juez_tipos(TablaControl):
    n_id_juez_tipo = models.AutoField(primary_key=True)
    x_descripcion = models.CharField(max_length=100)

    class Meta:
        db_table = 'mae_est_juez_tipos'

#! ====================================================================
#! TABLA JUECES
#! ====================================================================
class mae_est_jueces(TablaControl):
    n_id_juez = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(usuario, on_delete=models.CASCADE)
    n_id_juez_tipo = models.ForeignKey(mae_est_juez_tipos,on_delete=models.CASCADE)
    l_activo = models.CharField(max_length=1,default='S')
    class Meta:
        db_table = 'mae_est_jueces'
        permissions = [
            ("list_mae_est_jueces", _("Listar Jueces")),
        ]

#! ====================================================================
#! TABLA INSTANCIA_JUECES
#! ====================================================================
class mov_est_instancia_jueces(TablaControl):
    n_id_instancia_juez = models.AutoField(primary_key=True)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    n_id_juez = models.ForeignKey(mae_est_jueces,on_delete = models.PROTECT)
    x_resolucion = models.CharField(max_length=200)
    x_pdf_res = models.FileField(upload_to='instancia/')
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_activo = models.CharField(max_length=1,default='S')
    class Meta:
        db_table = 'mov_est_instancia_jueces'

#! =====================================================================
#! TABLA ESPECIALIDADES
#! =====================================================================
class mae_est_especialidades(TablaControl):
    c_especialidad = models.CharField(max_length=2,primary_key=True)
    x_desc_especialidad = models.CharField(max_length=30)
    c_cod_especialidad = models.CharField(max_length=2)
    class Meta:
        db_table = 'mae_est_especialidades'

#! =====================================================================
#! TABLA SUB_ESPECIALIDAD_EST - MOD 28/02/2025
#! =====================================================================
class mae_est_sub_especialidad_ests(TablaControl):
    c_sub_esp = models.CharField(max_length=2,primary_key=True)
    x_sub_esp = models.CharField(max_length=30)
    class Meta:
        db_table = 'mae_est_sub_especialidad_ests'

#! =====================================================================
#! TABLA ACTO_PROCESAL
#! =====================================================================
class mae_est_acto_procesales(TablaControl):
    c_acto_procesal = models.CharField(max_length=3,primary_key=True)
    c_org_jurisd = models.ForeignKey(mae_est_organo_jurisdiccionales,on_delete=models.PROTECT)
    c_especialidad = models.ForeignKey(mae_est_especialidades,on_delete=models.PROTECT)
    x_desc_acto_procesal=models.CharField(max_length=150)
    l_activo = models.CharField(max_length=1,default='S',null=True)
    class Meta:
        db_table = 'mae_est_acto_procesales'

#! =====================================================================
#! TABLA VARIABLES
#! =====================================================================
class mae_est_variables(TablaControl):
    var_id = models.IntegerField(primary_key=True)
    var_des = models.CharField(max_length=80)
    var_ord = models.IntegerField()
    var_letra = models.CharField(max_length=2)
    c_estadistica = models.CharField(max_length=5)
    var_ind = models.CharField(max_length=1)
    var_des_det = models.CharField(max_length=255,null=True)
    var_lines_inf = models.CharField(max_length=1, null=True)
    class Meta:
        db_table = 'mae_est_variables'

#! =====================================================================
#! TABLA VARIABL_PERIODOS - MOD 28/02/2025
#! =====================================================================
class mov_est_var_periodos(TablaControl):
    id_var_periodos=models.AutoField(primary_key=True)
    n_anio_est = models.IntegerField()
    n_mes_est = models.IntegerField()
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    n_dependencia = models.IntegerField()
    c_especialidad = models.ForeignKey(mae_est_especialidades,on_delete=models.PROTECT)
    var = models.ForeignKey(mae_est_variables,on_delete=models.PROTECT)
    n_funcion = models.IntegerField()
    c_sub_especialidad = models.ForeignKey(mae_est_sub_especialidad_ests,on_delete=models.PROTECT)
    n_cant_var = models.IntegerField()
    
    #x_formato = models.CharField(max_length=500, null=True)
    class Meta:
        db_table = 'mov_est_var_periodos'

#! ===============================================================================================================
#! TABLA MAESTRA RESUMEN
#! ================================================================================================================
class mae_est_meta_resumenes(TablaControl):
    n_id_meta_resumen = models.AutoField(primary_key=True)
    n_anio_est = models.IntegerField()
    n_mes_est = models.IntegerField()
    n_id_modulo = models.ForeignKey(mae_est_modulos,on_delete=models.PROTECT)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    m_estandar_prod = models.IntegerField()
    n_carg_procesal_ini = models.IntegerField()
    m_t_resuelto = models.IntegerField()
    m_t_ingreso = models.IntegerField()
    m_t_ingreso_proy = models.IntegerField()
    m_ing_proyectado = models.IntegerField()
    m_carg_procesal_tram = models.IntegerField()
    m_carg_procesal_min = models.IntegerField()
    m_carg_procesal_max = models.IntegerField()
    m_egre_otra_dep = models.IntegerField()
    m_ing_otra_dep = models.IntegerField()
    m_pend_reserva = models.IntegerField()
    m_meta_preliminar = models.IntegerField()
    x_situacion_carga = models.CharField(max_length=20)
    m_avan_meta = models.DecimalField(max_digits=5,decimal_places=2)
    m_ideal_avan_meta = models.IntegerField()
    m_ideal_avan_meta_ant = models.IntegerField(null = True)
    x_niv_produc = models.CharField(max_length=20)
    m_niv_bueno = models.IntegerField()
    m_niv_muy_bueno = models.IntegerField()
    f_fecha_mod = models.DateTimeField(auto_now=True)
    l_estado = models.CharField(max_length=1,default='A',null=True)
    
    class Meta:
        db_table = 'mae_est_meta_resumenes'

#! =====================================================================
#! TABLA MAESTRA RESUMEN MODIFICADO
#! =====================================================================
class mae_est_meta_resumenes_modificado(TablaControl):
    n_id_meta_resumen_mod = models.AutoField(primary_key=True)
    n_anio_est = models.IntegerField()
    n_mes_est = models.IntegerField()
    n_id_modulo = models.ForeignKey(mae_est_modulos,on_delete=models.PROTECT)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    m_estandar_prod = models.IntegerField()
    n_carg_procesal_ini = models.IntegerField()
    m_t_resuelto = models.IntegerField()
    m_t_ingreso = models.IntegerField()
    m_t_ingreso_proy = models.IntegerField()
    m_ing_proyectado = models.IntegerField()
    m_carg_procesal_tram = models.IntegerField()
    m_carg_procesal_min = models.IntegerField()
    m_carg_procesal_max = models.IntegerField()
    m_egre_otra_dep = models.IntegerField()
    m_ing_otra_dep = models.IntegerField()
    m_pend_reserva = models.IntegerField()
    m_meta_preliminar = models.IntegerField()
    x_situacion_carga = models.CharField(max_length=20)
    m_avan_meta = models.DecimalField(max_digits=5,decimal_places=2)
    m_ideal_avan_meta = models.IntegerField()
    m_ideal_avan_meta_ant = models.IntegerField(null = True)
    x_niv_produc = models.CharField(max_length=20)
    m_niv_bueno = models.IntegerField()
    m_niv_muy_bueno = models.IntegerField()
    f_fecha_mod = models.DateTimeField(auto_now=True)
    l_estado = models.CharField(max_length=1,default='T',null=True)
    m_op_egre_otra_dep = models.BooleanField(default=False)
    m_op_ing_otra_dep  = models.BooleanField(default=False)
    m_op_pend_reserva  = models.BooleanField(default=False)
    n_valor_modificado = models.IntegerField(null=True,blank=True)
    n_meta_opj = models.IntegerField(null=True,blank=True)
    l_corte = models.CharField(max_length=1, default='Q', null=True)

    class Meta:
        db_table = 'mae_est_meta_resumenes_modificado'
        constraints = [
            models.UniqueConstraint(
                fields=['n_anio_est', 'n_mes_est', 'n_id_modulo', 'n_instancia', 'l_corte'],
                name='uq_modificado_periodo_modulo_instancia_corte'
            )
        ]
        indexes = [
            models.Index(fields=['n_anio_est', 'n_mes_est', 'l_corte']),
            models.Index(fields=['n_id_modulo', 'n_instancia', 'l_corte']),
        ]

#* =====================================================================
#* AUDITORIA DE TABLA  MAE_EST_META_RESUMENES_MODIFICADO
#* =====================================================================
class aud_mae_est_meta_resumenes_modificado(TablaControl, TablaAuditoria):
    n_id_meta_resumen = models.IntegerField()
    n_anio_est = models.IntegerField()
    n_mes_est = models.IntegerField()
    n_id_modulo = models.ForeignKey(mae_est_modulos,on_delete=models.PROTECT)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.PROTECT)
    m_estandar_prod = models.IntegerField()
    n_carg_procesal_ini = models.IntegerField()
    m_t_resuelto = models.IntegerField()
    m_t_ingreso = models.IntegerField()
    m_t_ingreso_proy = models.IntegerField()
    m_ing_proyectado = models.IntegerField()
    m_carg_procesal_tram = models.IntegerField()
    m_carg_procesal_min = models.IntegerField()
    m_carg_procesal_max = models.IntegerField()
    m_egre_otra_dep = models.IntegerField()
    m_ing_otra_dep = models.IntegerField()
    m_pend_reserva = models.IntegerField()
    m_meta_preliminar = models.IntegerField()
    x_situacion_carga = models.CharField(max_length=20)
    m_avan_meta = models.DecimalField(max_digits=5,decimal_places=2)
    m_ideal_avan_meta = models.IntegerField()
    m_ideal_avan_meta_ant = models.IntegerField(null = True)
    x_niv_produc = models.CharField(max_length=20)
    m_niv_bueno = models.IntegerField()
    m_niv_muy_bueno = models.IntegerField()
    f_fecha_mod = models.DateTimeField(auto_now=True)
    l_estado = models.CharField(max_length=1,default='A',null=True)
    
    class Meta:
        db_table = 'aud_mae_est_meta_resumenes_modificado'

#! ====================================================================
#! TABLA INSTANCIA_ESCALAS
#! ====================================================================
class mae_est_meta_detalles(TablaControl):
    n_id_meta_detalle = models.AutoField(primary_key=True)
    n_anio_est = models.IntegerField(null=True)
    n_mes_est = models.IntegerField(null = True)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.CASCADE)
    m_t_resuelto_mes = models.IntegerField(null = True)
    m_t_ingreso_mes = models.IntegerField(null = True)
    c_especialidad = models.ForeignKey(mae_est_especialidades,on_delete=models.CASCADE)
    f_fecha_mod = models.DateTimeField(auto_now=True,null = True)
 
    class Meta:
        db_table = 'mae_est_meta_detalles'

#! ====================================================================
#! TABLA MAE_EST_ESTAND_PROD

#! ====================================================================
class mae_est_estand_prod(TablaControl):
    n_id_estand_prod = models.AutoField(primary_key=True)
    x_resolucion = models.CharField(max_length=200)
    x_prd_res = models.FileField(upload_to='resoluciones/estandar/')
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_activo = models.CharField(max_length=1,default='S')

    class Meta:
        db_table = 'mae_est_estand_prod'

#! ====================================================================
#! TABLA MAE_EST_INSTANCIA_ESTANDAR
#! ====================================================================
class mae_est_instancia_estandares(TablaControl):
    n_id_instancia_estandar = models.AutoField(primary_key=True)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.CASCADE)
    n_id_estand_prod = models.ForeignKey(mae_est_estand_prod,on_delete=models.CASCADE)
    m_estandar_prod = models.DecimalField(max_digits=7,decimal_places=2)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_activo = models.CharField(max_length=1,default='S')
 
    class Meta:
        db_table = 'mae_est_instancia_estandares'

class conf_est_meta_conf(TablaControl):
    n_id_meta_config = models.AutoField(primary_key=True)
    n_instancia = models.ForeignKey(mae_est_instancia,on_delete=models.CASCADE)
    usuario = models.ForeignKey(usuario,on_delete=models.PROTECT, null=True )
    n_anio_est = models.IntegerField()
    n_mes_est = models.IntegerField()
    m_op_egre_otra_dep = models.IntegerField()
    m_op_ing_otra_dep = models.IntegerField()
    m_op_pend_reserva = models.IntegerField()
    f_fecha_mod = models.DateTimeField(null = True)

    class Meta:
        db_table = 'conf_est_meta_conf'

#! ====================================================================
#! TABLA MOV_EST_MODULO_USUARIOS
#! ====================================================================
class mov_est_modulo_usuarios(TablaControl):
    n_id_modulo_usuario = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(usuario, on_delete=models.CASCADE)
    n_id_modulo = models.ForeignKey(mae_est_modulos,on_delete=models.CASCADE)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)
    f_fecha_baja = models.DateTimeField(null = True)
    l_activo = models.CharField(max_length=1,default='S')

    class Meta:
        db_table = 'mov_est_modulo_usuarios'
        permissions = [
            ("list_mov_est_modulo_usuarios", _("Listar Administrador Módulos")),
        ]

class hst_usuario_accion(TablaControl):
    usuario = models.ForeignKey(usuario, on_delete=models.CASCADE)
    x_accion = models.CharField(max_length=100)
    f_fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.x_accion} - {self.f_fecha_creacion}"

    def save(self, *args, **kwargs):
        self.x_accion = self.x_accion.upper()
        super(hst_usuario_accion, self).save(*args, **kwargs)

    class Meta:
        db_table = 'hst_usuario_accion'
        permissions = [
            ("list_hst_usuario_accion", _("Listar Usuario Accion")),
        ]


class mae_est_civil_meta_pre(TablaControl):
    n_id_civil_meta_pre = models.AutoField(primary_key=True)
    n_instancias_id = models.IntegerField()
    n_meta_preliminar_ci = models.IntegerField()

    class Meta:
        db_table = 'mae_est_civil_meta_pre'

class mae_est_sub_especilidad(TablaControl):
    n_id_sub_esp = models.AutoField(primary_key=True)
    c_sub_esp = models.CharField(max_length=2)
    x_sub_esp = models.CharField(max_length=100)
    n_orden = models.IntegerField()
    l_activo = models.CharField(max_length=1,default='S')

    class Meta:
        db_table = 'mae_est_sub_especilidad'