from django.db import models
from django.contrib.auth.models import User
from datetime import date 

class CatDireccion(models.Model):
    nombre_direccion = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_direccion

# ==========================================
# 1. EVOLUCIÓN: ROLES JERÁRQUICOS
# ==========================================
ROLES_JERARQUIA = (
    ('Director', 'Director de Área'),
    ('Subdirector', 'Subdirector / Jefe de Departamento'),
    ('Coordinador', 'Coordinador / Cuadrilla Operativa'),
)

class PerfilAgente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion_asignada = models.ForeignKey(CatDireccion, on_delete=models.SET_NULL, null=True, blank=True)
    # Nuevo campo para el flujo 4D
    rol = models.CharField(max_length=50, choices=ROLES_JERARQUIA, default='Coordinador')
    
    def __str__(self):
        return f"{self.get_rol_display()} - {self.usuario.username} ({self.direccion_asignada})"

class CatColonia(models.Model):
    nombre_colonia = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre_colonia

class TicketAyuda(models.Model):
    folio = models.CharField(max_length=20, primary_key=True, blank=True)
    fecha = models.DateField(auto_now_add=True) 
    
    # 👇 NUEVOS CAMPOS DE NOMBRE 👇
    nombre = models.CharField(max_length=100, verbose_name="Nombre(s)")
    apellido_paterno = models.CharField(max_length=100, verbose_name="Apellido Paterno")
    apellido_materno = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellido Materno (Opcional)")
    
    asunto = models.CharField(max_length=150, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    colonia = models.ForeignKey(CatColonia, on_delete=models.SET_NULL, null=True)
    
    # 👇 NUEVOS CAMPOS DE DIRECCIÓN FÍSICA 👇
    calle = models.CharField(max_length=150, blank=True, null=True, verbose_name="Calle/Avenida")
    numero_exterior = models.CharField(max_length=50, blank=True, null=True, verbose_name="Núm. Exterior")
    numero_interior = models.CharField(max_length=50, blank=True, null=True, verbose_name="Núm. Interior (Opcional)")
    
    email = models.EmailField(max_length=150, blank=True, null=True, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.ForeignKey(CatDireccion, on_delete=models.SET_NULL, null=True, verbose_name="Dependencia")
    observaciones = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Nuevo')
    latitud = models.CharField(max_length=50, blank=True, null=True)
    longitud = models.CharField(max_length=50, blank=True, null=True)
    evidencia = models.FileField(upload_to='evidencias/', blank=True, null=True)

    agente_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='mis_tickets')
    director_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_como_director')
    subdirector_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_como_subdirector')
    coordinador_asignado = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_como_coordinador')

    porcentaje_avance = models.IntegerField(default=0)
    notas_agente = models.TextField(blank=True, null=True)
    gestor = models.CharField(max_length=200, blank=True, null=True, verbose_name="Gestor (Dejar en blanco si es Ciudadano Directo)")

    # 👇 PROPIEDADES FANTASMAS (Para no romper el front-end) 👇
    @property
    def nombre_completo(self):
        materno = f" {self.apellido_materno}" if self.apellido_materno else ""
        return f"{self.nombre} {self.apellido_paterno}{materno}"

    @property
    def direccion_completa(self):
        ext = f" No. {self.numero_exterior}" if self.numero_exterior else ""
        int_num = f" Int. {self.numero_interior}" if self.numero_interior else ""
        return f"{self.calle}{ext}{int_num}".strip()

    def save(self, *args, **kwargs):
        if not self.folio:
            total_tickets = TicketAyuda.objects.count()
            self.folio = str(total_tickets + 1000)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.folio} - {self.nombre_completo}"

    @property
    def dias_abierto(self):
        if self.fecha:
            return (date.today() - self.fecha).days
        return 0
# ==========================================
# 3. EVOLUCIÓN: CHECKLIST DE TAREAS (MOTOR 4D)
# ==========================================
class TareaTicket(models.Model):
    ticket = models.ForeignKey(TicketAyuda, on_delete=models.CASCADE, related_name='tareas')
    descripcion = models.CharField(max_length=255)
    completada = models.BooleanField(default=False)
    evidencia_tarea = models.FileField(upload_to='evidencias_tareas/', blank=True, null=True)
    
    # Registramos qué usuario específico completó esta subtarea
    ejecutor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        estado = "✅" if self.completada else "⏳"
        return f"{estado} {self.descripcion} (Folio: {self.ticket.folio})"


class CopacisyDelegados(models.Model):
    Nombre = models.CharField(max_length=255)
    Apellidos = models.CharField(max_length=255)
    Seccion = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.Nombre} {self.Apellidos}"
