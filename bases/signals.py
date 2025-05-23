from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import hst_usuario_accesos
from django.utils.timezone import now

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    # Obtener la IP del usuario
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    # Crear un registro en la base de datos
    hst_usuario_accesos.objects.create(usuario=user, x_ip=ip)
    