from django import forms
from .models import *

class TicketForm(forms.ModelForm):
    # 👇 Ordenado alfabéticamente
    colonia = forms.ModelChoiceField(
        queryset=CatColonia.objects.all().order_by('nombre_colonia'),
        empty_label="--- Selecciona una Colonia ---",
        widget=forms.Select(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;'})
    )

    # AGREGAR ESTE NUEVO CAMPO:
    colonia_ciudadano = forms.ModelChoiceField(
        queryset=CatColonia.objects.all().order_by('nombre_colonia'),
        empty_label="--- Colonia del Solicitante ---",
        required=False,
        widget=forms.Select(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;'})
    )
    
    # 👇 Ordenado alfabéticamente
    direccion = forms.ModelChoiceField(
        queryset=CatDireccion.objects.all().order_by('nombre_direccion'),
        empty_label="--- Selecciona un Área ---",
        widget=forms.Select(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;'})
    )

    class Meta:
        model = TicketAyuda
        # 👇 AQUÍ ESTÁ EL TRUCO: El orden de esta lista define cómo se ve en el HTML 👇
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno', 'telefono', 'email',
            'colonia_ciudadano', 'calle_ciudadano', 'numero_exterior_ciudadano', 'numero_interior_ciudadano',
            'asunto', 'notas', 'direccion', 'via_entrada', 'numero_ocp', 'gestor',
            'colonia', 'calle', 'numero_exterior', 'numero_interior', 'latitud', 'longitud'
        ]
        
        widgets = {
            'latitud': forms.TextInput(attrs={'readonly': 'readonly'}), 
            'longitud': forms.TextInput(attrs={'readonly': 'readonly'}),
            'numero_ocp': forms.TextInput(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;', 'placeholder': 'Ej. OCP-2026-001'}),
            'gestor': forms.TextInput(attrs={'style': 'width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px;', 'placeholder': 'Ej. Juan Pérez (Dejar en blanco si es ciudadano directo)'}),
        }