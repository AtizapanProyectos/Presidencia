from django.contrib import admin
from .models import *

# -----------------------------------------------------
# 1. Catálogo de Colonias
# -----------------------------------------------------
@admin.register(CatColonia)
class CatColoniaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_colonia')
    search_fields = ('nombre_colonia',)
    ordering = ('nombre_colonia',)

# -----------------------------------------------------
# 2. Catálogo de Direcciones
# -----------------------------------------------------
@admin.register(CatDireccion)
class CatDireccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_direccion')
    search_fields = ('nombre_direccion',)

# -----------------------------------------------------
# 3. Perfil de Agentes (¡El gafete 4D!)
# -----------------------------------------------------
@admin.register(PerfilAgente)
class PerfilAgenteAdmin(admin.ModelAdmin):
    # Ahora mostramos el Rol (Director, Subdirector, Coordinador)
    list_display = ('usuario', 'rol', 'direccion_asignada')
    
    # Agregamos el rol a los filtros laterales
    list_filter = ('rol', 'direccion_asignada')
    
    # Buscador
    search_fields = ('usuario__username', 'direccion_asignada__nombre_direccion')

# -----------------------------------------------------
# 4. Tareas del Ticket (El Checklist 4D)
# -----------------------------------------------------
# Truco: Esto hace que las tareas aparezcan DENTRO del ticket en el Admin
class TareaTicketInline(admin.TabularInline):
    model = TareaTicket
    extra = 0 # No agregar filas vacías por defecto
    readonly_fields = ('fecha_creacion', 'fecha_completada', 'ejecutor')
    fields = ('descripcion', 'completada', 'ejecutor', 'evidencia_tarea', 'fecha_creacion', 'fecha_completada')

# Por si quieres ver todas las tareas sueltas en una lista maestra
@admin.register(TareaTicket)
class TareaTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'descripcion', 'completada', 'ejecutor')
    list_filter = ('completada', 'fecha_creacion')
    search_fields = ('descripcion', 'ticket__folio')

# -----------------------------------------------------
# 5. Tickets de Mesa de Ayuda (¡El principal!)
# -----------------------------------------------------
@admin.register(TicketAyuda)
class TicketAyudaAdmin(admin.ModelAdmin):
    # Columnas que se van a ver en la lista principal (agregué el porcentaje)
    list_display = ('folio', 'fecha', 'nombre', 'asunto', 'direccion', 'status', 'porcentaje_avance')
    
    # Filtros laterales para buscar rápido
    list_filter = ('status', 'direccion', 'colonia', 'fecha')
    
    # Barra de búsqueda
    search_fields = ('folio', 'nombre', 'asunto', 'notas', 'telefono')
    
    # ¡Truco genial! Permite cambiar el status sin tener que abrir el ticket
    list_editable = ('status',) 
    
    # Un menú estilo calendario arriba de la lista
    date_hierarchy = 'fecha'
    
    # Agregamos las tareas incrustadas al final del ticket
    inlines = [TareaTicketInline]
    
    # Opcional: Para organizar mejor la vista de detalle en el admin
    fieldsets = (
        ('Información del Ciudadano', {
            'fields': ('folio', 'nombre', 'telefono', 'colonia', 'domicilio')
        }),
        ('Detalles del Reporte', {
            'fields': ('asunto', 'notas', 'direccion', 'latitud', 'longitud', 'evidencia')
        }),
        ('Estado Operativo 4D', {
            'fields': ('status', 'porcentaje_avance', 'notas_agente')
        }),
        ('Asignación Jerárquica (Nuevos)', {
            'fields': ('director_asignado', 'subdirector_asignado', 'coordinador_asignado', 'agente_asignado')
        }),
    )

@admin.register(CopacisyDelegados)
class CopacisyDelegadosAdmin(admin.ModelAdmin):
    # Columnas que se muestran en la lista
    list_display = ('Nombre', 'Apellidos', 'Seccion')

    # Filtros laterales
    list_filter = ('Seccion',)

    # Buscador
    search_fields = ('Nombre', 'Apellidos', 'Seccion')