# utils_auditoria.py (o donde prefieras)
from django.utils import timezone

def marcar_audit(instance, user, tipo: str):
    """
    tipo: 'I' | 'U' | 'D'
    Setea campos de auditoría de app (b_aud, c_aud_uid, etc.).
    El b_trns y f_trns lo maneja el TRIGGER en BD.
    """
    if hasattr(instance, 'b_aud'):
        instance.b_aud = tipo

    # Si tu TablaControl tiene c_aud_uid como FK a usuario:
    if hasattr(instance, 'c_aud_uid'):
        try:
            instance.c_aud_uid = user   # FK a User
        except Exception:
            # Si lo cambiaste a CharField, guarda username
            try:
                instance.c_aud_uid = getattr(user, 'username', str(user))
            except Exception:
                pass

    if hasattr(instance, 'c_aud_uidred'):
        instance.c_aud_uidred = getattr(user, 'username', None) or str(user)

    if hasattr(instance, 'f_aud'):
        instance.f_aud = timezone.now()