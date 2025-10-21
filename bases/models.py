from django.db import models
from django.utils.timezone import localtime
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser, Group

class TablaControl(models.Model):
    f_aud = models.DateTimeField(auto_now=True, null=True, blank=True)
    b_aud = models.CharField(max_length=1, default='I', null=True)
    c_aud_uid = models.CharField(max_length=30, null=True, blank=True)
    c_aud_uidred = models.CharField(max_length=30, null=True, blank=True)
    c_aud_pc = models.CharField(max_length=30, null=True, blank=True)
    n_aud_ip = models.GenericIPAddressField(null=True, blank=True)
    c_aud_mcaddr = models.CharField(max_length=17, null=True, blank=True)

    class Meta:
        abstract = True

class TablaAuditoria(models.Model):
    n_trns_id = models.AutoField(primary_key=True)
    f_trns = models.DateTimeField(auto_now_add=True)
    b_trns = models.CharField(max_length=1)
    c_trns_uid = models.CharField(max_length=30, null=True, blank=True)
    c_trns_pc = models.CharField(max_length=30, null=True, blank=True)
    n_trns_ip =  models.GenericIPAddressField(null=True, blank=True)
    c_trns_mcaddr = models.CharField(max_length=17, null=True, blank=True)

    class Meta:
        abstract = True

class mae_est_sexos(TablaControl):
    n_id_sexo = models.AutoField(primary_key=True)
    x_descripcion = models.CharField(max_length=20)


    class Meta:
        db_table = 'mae_est_sexos'

    def __str__(self):
        return self.x_descripcion
    
class usuario(AbstractUser):
    x_dni = models.CharField(max_length=8, unique=True, default='00000000')
    x_nombres = models.CharField(max_length=50)
    x_app_paterno = models.CharField(max_length=40)
    x_app_materno = models.CharField(max_length=40)
    x_telefono = models.CharField(max_length=15, blank=True, null=True)
    n_id_sexo = models.ForeignKey(mae_est_sexos, null=True, blank=True, on_delete=models.SET_NULL)
    profile_image = models.ImageField(upload_to='img_perfil/', default='img_perfil/perfil.png',blank=True,null=True)
    l_mensaje = models.BooleanField(default=False)
    f_aud = models.DateTimeField(auto_now=True, null=True, blank=True)
    b_aud = models.CharField(max_length=1, default='I', null=True)
    c_aud_uid = models.CharField(max_length=30, null=True, blank=True)
    c_aud_uidred = models.CharField(max_length=30, null=True, blank=True)
    n_aud_ip = models.GenericIPAddressField(null=True, blank=True)
    c_aud_mcaddr = models.CharField(max_length=17, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        through='mae_est_usuarios_groups',
        related_name='usuario_set',
    )
    last_name = None
    first_name = None

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['x_dni', 'x_nombres', 'x_app_paterno', 'x_app_materno', 'email']

    def save(self, *args, **kwargs):
        self.x_nombres = self.x_nombres.upper()
        self.x_app_paterno = self.x_app_paterno.upper()
        self.x_app_materno = self.x_app_materno.upper()
        super(usuario, self).save(*args, **kwargs)

    class Meta:
        db_table = 'mae_est_usuarios'

class mae_est_usuarios_groups(TablaControl):
    n_id_usuario_group = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(usuario, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    

    class Meta:
        db_table = 'mae_est_usuarios_groups'


class hst_usuario_accesos(models.Model):
    usuario = models.ForeignKey(usuario, on_delete=models.CASCADE, related_name='login_records')
    f_fecha_hora = models.DateTimeField(auto_now_add=True)
    x_ip = models.GenericIPAddressField()
    
    def __str__(self):
        local_timestamp = localtime(self.f_fecha_hora)                                                             # Convertir a la zona horaria local
        return f"{self.usuario.x_app_paterno} - {local_timestamp} - {self.x_ip}"
    
    class Meta:
        db_table = 'hst_usuario_accesos'
