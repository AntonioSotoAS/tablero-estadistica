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
    class Meta:
        model = usuario
        fields = ['x_app_paterno','x_app_materno','x_nombres','n_id_sexo','x_dni','email','username','password','profile_image']
        widgets = {'password': forms.PasswordInput(),
            'email': forms.EmailInput(),
            'x_app_paterno':forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Ingrese su Apellido Paterno',
                'style':'text-transform:uppercase'
                }),
            'x_app_materno':forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Ingrese su Apellido Materno',
                'style':'text-transform:uppercase'
                }),
            'x_nombres':forms.TextInput(attrs={
                'class':'form-control',
                'placeholder':'Ingrese su Nombre',
                'style':'text-transform:uppercase'
                }),
            'n_id_sexo':Select2Widget(attrs={'class':'form-control'})}
        
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter (self.fields):
            self.fields[field].widget.attrs.update({
                'class':'form-control',
                'placeholder': f'Ingrese {field.replace("_", " ")}',
            })
            self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
            })
            self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingrese su correo electrónico',
            'type': 'email',  # Tipo email
            })

class UsuarioEditForm(forms.ModelForm):
    class Meta:
        model = usuario
        fields = ['x_app_paterno','x_app_materno','x_nombres','n_id_sexo','x_dni','email','username','profile_image']
        widgets = {'password': forms.PasswordInput(),
            'email': forms.EmailInput(),
            'n_id_sexo':Select2Widget(attrs={'class':'form-control'})}
        
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter (self.fields):
            self.fields[field].widget.attrs.update({
                'class':'form-control',
                'placeholder': f'Ingrese {field.replace("_", " ")}',
            })
            self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ingrese su correo electrónico',
            'type': 'email',  # Tipo email
            })


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