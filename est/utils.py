# est/utils.py
from django.db import transaction
from .models import (
    mae_est_meta_resumenes,
    mae_est_meta_resumenes_modificado,
)

@transaction.atomic
def crear_snapshot_modificado(period_year: int, period_month: int) -> int:
    """
    Crea (si falta) registros en mae_est_meta_resumenes_modificado copiando
    desde mae_est_meta_resumenes para (año, mes). Devuelve cuántos creó.
    """
    base_qs = (
        mae_est_meta_resumenes.objects
        .filter(n_anio_est=period_year, n_mes_est=period_month)
        .select_related('n_instancia', 'n_id_modulo')
    )

    existentes = set(
        mae_est_meta_resumenes_modificado.objects
        .filter(n_anio_est=period_year, n_mes_est=period_month)
        .values_list('n_instancia_id', 'n_id_modulo_id')
    )

    to_create = []
    for r in base_qs:
        key = (r.n_instancia_id, r.n_id_modulo_id)
        if key in existentes:
            continue
        to_create.append(mae_est_meta_resumenes_modificado(
            n_anio_est=r.n_anio_est,
            n_mes_est=r.n_mes_est,
            n_id_modulo=r.n_id_modulo,
            n_instancia=r.n_instancia,
            m_estandar_prod=r.m_estandar_prod,
            n_carg_procesal_ini=r.n_carg_procesal_ini,
            m_t_resuelto=r.m_t_resuelto,
            m_t_ingreso=r.m_t_ingreso,
            m_t_ingreso_proy=r.m_t_ingreso_proy,
            m_ing_proyectado=r.m_ing_proyectado,
            m_carg_procesal_tram=r.m_carg_procesal_tram,
            m_carg_procesal_min=r.m_carg_procesal_min,
            m_carg_procesal_max=r.m_carg_procesal_max,
            m_egre_otra_dep=r.m_egre_otra_dep,
            m_ing_otra_dep=r.m_ing_otra_dep,
            m_pend_reserva=r.m_pend_reserva,
            m_meta_preliminar=r.m_meta_preliminar,
            x_situacion_carga=r.x_situacion_carga,
            m_avan_meta=r.m_avan_meta,
            m_ideal_avan_meta=r.m_ideal_avan_meta,
            m_ideal_avan_meta_ant=r.m_ideal_avan_meta_ant,
            x_niv_produc=r.x_niv_produc,
            m_niv_bueno=r.m_niv_bueno,
            m_niv_muy_bueno=r.m_niv_muy_bueno,
            l_estado='T',
            m_op_egre_otra_dep=False,
            m_op_ing_otra_dep=False,
            m_op_pend_reserva=False,
            n_valor_modificado=None,
            n_meta_opj=None,
        ))
    if to_create:
        mae_est_meta_resumenes_modificado.objects.bulk_create(to_create, ignore_conflicts=True)
    return len(to_create)
