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
    list_display = ('usuario', 'rol', 'direccion_asignada')
    list_filter = ('rol', 'direccion_asignada')
    search_fields = ('usuario__username', 'direccion_asignada__nombre_direccion')

# -----------------------------------------------------
# 4. Tareas del Ticket (El Checklist 4D)
# -----------------------------------------------------
class TareaTicketInline(admin.TabularInline):
    model = TareaTicket
    extra = 0 # No agregar filas vacías por defecto
    readonly_fields = ('fecha_creacion', 'fecha_completada', 'ejecutor')
    fields = ('descripcion', 'completada', 'ejecutor', 'evidencia_tarea', 'fecha_creacion', 'fecha_completada')

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
    # Usamos la nueva función para mostrar el nombre completo en la tabla
    list_display = ('folio', 'fecha', 'mostrar_nombre_completo', 'asunto', 'direccion', 'status', 'porcentaje_avance')
    
    list_filter = ('status', 'direccion', 'colonia', 'fecha')
    
    # Actualizamos el buscador con los nuevos campos
    search_fields = ('folio', 'nombre', 'apellido_paterno', 'apellido_materno', 'asunto', 'notas', 'telefono', 'calle')
    
    list_editable = ('status',) 
    date_hierarchy = 'fecha'
    inlines = [TareaTicketInline]
    
    # Reorganizamos los fieldsets de forma profesional
    fieldsets = (
        ('Información del Ciudadano', {
            'fields': (
                'folio', 
                ('nombre', 'apellido_paterno', 'apellido_materno'), # Los agrupa en una fila
                'telefono', 'gestor'
            )
        }),
        ('Ubicación Física', {
            'fields': (
                'colonia', 
                ('calle', 'numero_exterior', 'numero_interior') # Los agrupa en una fila
            )
        }),
        ('Detalles del Reporte', {
            'fields': ('asunto', 'notas', 'direccion', 'latitud', 'longitud', 'evidencia')
        }),
        ('Estado Operativo 4D', {
            'fields': ('status', 'porcentaje_avance', 'notas_agente')
        }),
        ('Asignación Jerárquica', {
            'fields': ('director_asignado', 'subdirector_asignado', 'coordinador_asignado', 'agente_asignado')
        }),
    )

    # Función que renderiza la propiedad del modelo en el list_display
    def mostrar_nombre_completo(self, obj):
        return obj.nombre_completo
    mostrar_nombre_completo.short_description = 'Ciudadano'

# -----------------------------------------------------
# 6. Gestores (Copacis y Delegados)
# -----------------------------------------------------
@admin.register(CopacisyDelegados)
class CopacisyDelegadosAdmin(admin.ModelAdmin):
    list_display = ('Nombre', 'Apellidos', 'Seccion')
    list_filter = ('Seccion',)
    search_fields = ('Nombre', 'Apellidos', 'Seccion')