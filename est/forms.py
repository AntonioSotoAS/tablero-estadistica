from django import forms
from .models import  mae_est_modulos, mae_est_jueces, mae_est_usuarios_groups, mov_est_estprod_anuales,mae_est_escala_detalle,\
                    mov_est_instancia_jueces

#! =============================================
#! ================== MODULOS ==================
#! =============================================
class ModuloForm(forms.ModelForm):
    class Meta:
        model = mae_est_modulos
        fields = ['x_nombre']
        labels = {
            'x_nombre': "Ingresar Nombre del Modulo",
        }
        widgets = {
            'x_nombre': forms.TextInput(attrs={
                'placeholder': "Ingresar Nombre de Modulo",
                'class': 'form-control',
                'style': 'text-transform: uppercase;',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })

#! =============================================
#! ==================== JUEZ ===================
#! =============================================
class JuezForm(forms.ModelForm):
    class Meta:
        model = mae_est_jueces
        fields = ['usuario', 'n_id_juez_tipo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })

#! =============================================
#! ============== JUEZ INSTANCIA ===============
#! =============================================
class AsignacionJuezForm(forms.ModelForm):
    class Meta:
        model = mov_est_instancia_jueces
        fields = ['n_instancia', 'n_id_juez', 'x_resolucion', 'x_pdf_res']

#! =============================================
#! ============== ESCALA DETALLE ===============
#! =============================================
class EscalaDetalleForm(forms.ModelForm):
    class Meta:
        model = mae_est_escala_detalle
        fields = ['x_mes', 'm_porcentaje']
        widgets = {
            'x_mes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mes'}),
            'm_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Porcentaje'}),
        }


#! =============================================
#! ======== ESTANDAR PRODUCCION ANUAL ==========
#! =============================================
class EstProdAnualForm(forms.ModelForm):
    class Meta:
        model = mov_est_estprod_anuales
        fields = [
            'n_instancia',
            'm_estandar_prod',
            'm_carga_min',
            'm_carga_max',
            'm_meta_preliminar',
            'm_meta_final',
            'l_org_penal',
            'l_unico_especialidad',
            'l_volencia_familiar',
            'l_activo',
        ]
        widgets = {
            'n_instancia': forms.Select(attrs={'class': 'form-control'}),
            'm_estandar_prod': forms.NumberInput(attrs={'class': 'form-control'}),
            'm_carga_min': forms.NumberInput(attrs={'class': 'form-control','placeholder':"Ingresar Carga Mínima"}),
            'm_carga_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'm_meta_preliminar': forms.NumberInput(attrs={'class': 'form-control'}),
            'm_meta_final': forms.NumberInput(attrs={'class': 'form-control'}),
            'l_org_penal': forms.Select(choices=[('S', 'Sí'), ('N', 'No')], attrs={'class': 'form-control'}),
            'l_unico_especialidad': forms.Select(choices=[('S', 'Sí'), ('N', 'No')], attrs={'class': 'form-control'}),
            'l_volencia_familiar': forms.Select(choices=[('S', 'Sí'), ('N', 'No')], attrs={'class': 'form-control'}),
            'l_activo': forms.Select(choices=[('S', 'Sí'), ('N', 'No')], attrs={'class': 'form-control'}),
        }