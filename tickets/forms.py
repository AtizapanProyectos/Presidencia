from django import forms
from .models import *

class TicketForm(forms.ModelForm):
    # 👇 Ordenado alfabéticamente
    colonia = forms.ModelChoiceField(
        queryset=CatColonia.objects.all().order_by('nombre_colonia'),
        empty_label="--- Selecciona una Colonia ---",
        widget=forms.Select(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;'})
    )
    
    # 👇 Ordenado alfabéticamente
    direccion = forms.ModelChoiceField(
        queryset=CatDireccion.objects.all().order_by('nombre_direccion'),
        empty_label="--- Selecciona un Área ---",
        widget=forms.Select(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;'})
    )

    # ❌ ELIMINAMOS LA VARIABLE "gestor" QUE ESTABA AQUÍ PORQUE YA NO ES UN SELECT ❌

    class Meta:
        model = TicketAyuda
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno', 
            'asunto', 'notas', 'colonia', 
            'calle', 'numero_exterior', 'numero_interior', 
            'telefono', 'direccion', 'gestor', 'latitud', 'longitud',
            'email'
        ]
        # 👇 AGREGAMOS EL GESTOR AQUÍ PARA DARLE ESTILO Y PLACEHOLDER 👇
        widgets = {
            'latitud': forms.TextInput(attrs={'readonly': 'readonly'}), 
            'longitud': forms.TextInput(attrs={'readonly': 'readonly'}),
            'gestor': forms.TextInput(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;', 'placeholder': 'Ej. Juan Pérez (Dejar en blanco si es ciudadano directo)'}),
        }