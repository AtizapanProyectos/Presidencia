from django.urls import path
from . import views

urlpatterns = [
# La raíz ahora es el login
    path('', views.vista_login, name='login'), 
    
    # Las demás rutas se quedan igual
    path('home/', views.inicio, name='inicio'), 
    path('crear/', views.crear_ticket, name='crear_ticket'), 
    path('mi-panel/', views.panel_agente, name='panel_agente'),
    path('salir/', views.salir, name='salir'),
    path('api/corregir-texto/', views.corregir_texto_ia, name='corregir_texto_ia'),
    path('a/', views.hola_qr, name='hola_qr'),
    path('a', views.hola_qr),
]