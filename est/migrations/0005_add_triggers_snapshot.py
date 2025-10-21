from django.db import migrations

CREATE_TRIGGERS = r"""
DROP TRIGGER IF EXISTS bi_aud_mae_est_meta_resumenes_modificado;
DROP TRIGGER IF EXISTS bu_aud_mae_est_meta_resumenes_modificado;

CREATE TRIGGER bi_aud_mae_est_meta_resumenes_modificado
BEFORE INSERT ON aud_mae_est_meta_resumenes_modificado
FOR EACH ROW
BEGIN
  SET NEW.b_trns = 'I';
  SET NEW.f_trns = NOW();
  -- opcional: si quieres guardar usuario app (ver Opción C abajo)
  SET NEW.c_trns_uid = COALESCE(@app_username, CURRENT_USER());
END;

CREATE TRIGGER bu_aud_mae_est_meta_resumenes_modificado
BEFORE UPDATE ON aud_mae_est_meta_resumenes_modificado
FOR EACH ROW
BEGIN
  IF IFNULL(OLD.l_estado,'') <> 'D' AND NEW.l_estado='D' THEN
    SET NEW.b_trns='D';
  ELSE
    SET NEW.b_trns='U';
  END IF;
  SET NEW.f_trns = NOW();
  SET NEW.c_trns_uid = COALESCE(@app_username, CURRENT_USER());
END;
"""

DROP_TRIGGERS = r"""
DROP TRIGGER IF EXISTS bi_aud_mae_est_meta_resumenes_modificado;
DROP TRIGGER IF EXISTS bu_aud_mae_est_meta_resumenes_modificado;
"""

class Migration(migrations.Migration):
    dependencies = [
        ("est", "0004_aud_mae_est_meta_resumenes_modificado"),  
    ]
    operations = [
        migrations.RunSQL(sql=CREATE_TRIGGERS, reverse_sql=DROP_TRIGGERS),
    ]