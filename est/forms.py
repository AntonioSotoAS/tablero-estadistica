from django import forms
from django.utils.timezone import localtime, now
from django.forms import modelformset_factory
from .models import  mae_est_modulos, mae_est_jueces, mae_est_usuarios_groups, mov_est_estprod_anuales,mae_est_escala_detalle,\
                    mov_est_instancia_jueces, mov_est_instancia_modulos, mae_est_instancia,\
                    conf_est_meta_conf



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
#! ============ MODULOS INSTANCIAS =============
#! =============================================
class InstanciaModuloForm(forms.ModelForm):
    class Meta:
        model = mov_est_instancia_modulos
        fields = ["n_instancia"]  # <-- Quitamos l_activo

    def __init__(self, *args, **kwargs):
        self.modulo = kwargs.pop("modulo", None)
        super().__init__(*args, **kwargs)
        if self.modulo:
            usadas_ids = (
                mov_est_instancia_modulos.objects
                .filter(n_id_modulo=self.modulo, l_activo="S")
                .values_list("n_instancia_id", flat=True)
            )
            self.fields["n_instancia"].queryset = mae_est_instancia.objects.exclude(pk__in=usadas_ids)
        # Select2 attrs
        self.fields["n_instancia"].widget.attrs.update({
            "class": "form-select select2",
            "data-placeholder": "Seleccione una instancia",
            "data-width": "100%",
        })

    def clean(self):
        cleaned = super().clean()
        instancia = cleaned.get("n_instancia")
        if self.modulo and instancia:
            # Evita duplicados (si quieres, sólo activos)
            existe = mov_est_instancia_modulos.objects.filter(
                n_id_modulo=self.modulo,
                n_instancia=instancia
            ).exists()
            if existe:
                raise forms.ValidationError("Esta instancia ya está asociada a este módulo.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        # Seteamos el módulo y el activo por defecto
        obj.n_id_modulo = self.modulo
        obj.l_activo = 'S'
        if commit:
            obj.save()
        return obj

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

    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.f_fecha_creacion = localtime(now())
        if commit:
            instancia.save()
        return instancia

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

#! =============================================
#! ======== CONFIGURACION DE LA META ===========
#* Es para la configuración de la meta que hace
#* el área de estadistica.
#! =============================================
# Checkbox que SOLO marca si el valor real es 1/True (evita '0' como truthy)
class IntSwitch(forms.CheckboxInput):
    def __init__(self, attrs=None):
        super().__init__(attrs=attrs, check_test=lambda v: str(v) in ('1', 'True', 'true', 'on'))

class MetaConfForm(forms.ModelForm):
    # switches (checkbox) pero el modelo sigue siendo Integer
    m_op_egre_otra_dep = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    m_op_ing_otra_dep  = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    m_op_pend_reserva  = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))

    class Meta:
        model  = conf_est_meta_conf
        fields = ['m_op_egre_otra_dep','m_op_ing_otra_dep','m_op_pend_reserva']

    # inicializa: 1 => True; otro => False
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        inst = self.instance
        if inst and inst.pk:
            self.fields['m_op_egre_otra_dep'].initial = (inst.m_op_egre_otra_dep == 1)
            self.fields['m_op_ing_otra_dep'].initial  = (inst.m_op_ing_otra_dep  == 1)
            self.fields['m_op_pend_reserva'].initial  = (inst.m_op_pend_reserva  == 1)

    # normaliza a 0/1
    def clean_m_op_egre_otra_dep(self): return 1 if self.cleaned_data.get('m_op_egre_otra_dep') else 0
    def clean_m_op_ing_otra_dep(self):  return 1 if self.cleaned_data.get('m_op_ing_otra_dep')  else 0
    def clean_m_op_pend_reserva(self):  return 1 if self.cleaned_data.get('m_op_pend_reserva') else 0

MetaConfFormSet = modelformset_factory(
    conf_est_meta_conf,
    form=MetaConfForm,
    extra=0,           # <-- SOLO editar, no crear
    can_delete=False,
)