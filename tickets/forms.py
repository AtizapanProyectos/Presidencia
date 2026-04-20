from django import forms
from .models import *

class TicketForm(forms.ModelForm):
    colonia = forms.ModelChoiceField(
        queryset=CatColonia.objects.all(),
        empty_label="--- Selecciona una Colonia ---",
        widget=forms.Select(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;'})
    )
    
    direccion = forms.ModelChoiceField(
        queryset=CatDireccion.objects.all(),
        empty_label="--- Selecciona un Área ---",
        widget=forms.Select(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;'})
    )

    # 👇 NUEVO SELECT PARA EL GESTOR 👇
    gestor = forms.ModelChoiceField(
        queryset=CopacisyDelegados.objects.all(),
        required=False, # Lo hace completamente opcional
        empty_label="--- Ninguno (Ciudadano Directo) ---",
        widget=forms.Select(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;'})
    )

    class Meta:
        model = TicketAyuda
        # 👇 IMPORTANTE: Añadimos 'gestor' a la lista de fields 👇
        fields = ['nombre', 'asunto', 'notas', 'colonia', 'domicilio', 'telefono', 'direccion', 'gestor', 'latitud', 'longitud']
        widgets = {
            'latitud': forms.TextInput(attrs={'readonly': 'readonly'}), 
            'longitud': forms.TextInput(attrs={'readonly': 'readonly'}),
        }