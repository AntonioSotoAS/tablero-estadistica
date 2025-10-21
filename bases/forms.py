from django import forms

#Importamos los Modelos
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django_select2.forms import Select2Widget
from .models import usuario

#Heredará el models form
#!====================================================
#!============UNIDADES ADMINISTRATIVAS ===============
#!====================================================
class UsuarioForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Ingrese su contraseña"})
    )

    class Meta:
        model = usuario
        fields = [
            'x_app_paterno','x_app_materno','x_nombres','n_id_sexo','x_dni',
            'email','username','password','profile_image','x_telefono','l_mensaje'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo electrónico'}),
            'n_id_sexo': Select2Widget(attrs={'class': 'form-select'}),

            # Campos de texto con upper excepto teléfono
            'x_app_paterno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su Apellido Paterno', 'style': 'text-transform:uppercase'}),
            'x_app_materno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su Apellido Materno', 'style': 'text-transform:uppercase'}),
            'x_nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su Nombre', 'style': 'text-transform:uppercase'}),
            'x_dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su DNI', 'maxlength': '8'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su usuario'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),

            # Teléfono: sin uppercase
            'x_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su Teléfono'}),

            # Switch para l_mensaje
            'l_mensaje': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        # Hashear contraseña
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
            # Si usas grupos intermedios u otras relaciones, guárdalas aquí
            self.save_m2m()
        return user


class UsuarioEditForm(forms.ModelForm):
    # Si quieres mostrar algo de contraseña (solo lectura), descomenta:
    # password = ReadOnlyPasswordHashField(label="Contraseña", help_text="Para cambiar la contraseña usa el formulario de cambio de contraseña.")

    class Meta:
        model = usuario
        fields = [
            'x_app_paterno','x_app_materno','x_nombres','n_id_sexo','x_dni',
            'email','username','profile_image','x_telefono','l_mensaje'
        ]
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su correo electrónico'}),
            'n_id_sexo': Select2Widget(attrs={'class': 'form-select'}),

            'x_app_paterno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su Apellido Paterno', 'style': 'text-transform:uppercase'}),
            'x_app_materno': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su Apellido Materno', 'style': 'text-transform:uppercase'}),
            'x_nombres': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su Nombre', 'style': 'text-transform:uppercase'}),
            'x_dni': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su DNI', 'maxlength': '8'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su usuario'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'x_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su Teléfono'}),
            'l_mensaje': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch'}),
        }


class UsuarioPassForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=128
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=128
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data
    
class PasswordChangeForm(DjangoPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Actualiza los labels de los campos
        self.fields['old_password'].label = 'Contraseña actual'
        self.fields['new_password1'].label = 'Nueva contraseña'
        self.fields['new_password2'].label = 'Confirmar nueva contraseña'

        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control mb-2',
            'placeholder': 'Ingrese su contraseña actual',
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control mb-2',
            'placeholder': 'Ingrese su nueva contraseña',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control mb-2',
            'placeholder': 'Confirme su nueva contraseña',
        })