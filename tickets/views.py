from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import *
from .forms import TicketForm
import json

def salir(request):
    logout(request)
    return redirect('login')

def vista_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('inicio')
        else:
            return redirect('panel_agente')

    if request.method == 'POST':
        formulario = AuthenticationForm(request, data=request.POST)
        if formulario.is_valid():
            usuario = formulario.get_user()
            login(request, usuario)
            if usuario.is_superuser:
                return redirect('inicio')
            else:
                return redirect('panel_agente')
    else:
        formulario = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': formulario})


@login_required(login_url='/')
def inicio(request):
    # --- PROCESAMIENTO DE ACCIONES (POST) ---
    if request.method == 'POST':
        folio_ticket = request.POST.get('folio_ticket')
        action = request.POST.get('action') # Capturamos la acción (aprobar o reasignar)
        
        if folio_ticket:
            # ESCENARIO A: EL ADMIN APRUEBA EL TICKET DEFINITIVAMENTE
# ESCENARIO A: EL ADMIN APRUEBA EL TICKET DEFINITIVAMENTE
            if action == 'aprobar_ticket':
                try:
                    ticket_aprobar = TicketAyuda.objects.get(folio=folio_ticket)
                    ticket_aprobar.status = 'Resuelto'
                    ticket_aprobar.porcentaje_avance = 100
                    nota_previa = ticket_aprobar.observaciones if ticket_aprobar.observaciones else ''
                    ticket_aprobar.observaciones = f"{nota_previa}\n\n[SISTEMA]: 🟢 Expediente validado y cerrado definitivamente por Alta Dirección el {timezone.now().strftime('%d/%m/%Y')}."
                    ticket_aprobar.save()
                except TicketAyuda.DoesNotExist:
                    pass
                return redirect('inicio')

            # ESCENARIO B: EL ADMIN DEVUELVE EL TICKET (NUEVO)
            elif action == 'rechazar_ticket':
                try:
                    ticket_rechazar = TicketAyuda.objects.get(folio=folio_ticket)
                    nota_rechazo = request.POST.get('notas_agente', 'Revisión requerida')
                    evidencia = request.FILES.get('evidencia_tarea')
                    
                    # 1. Creamos una nueva tarea para obligar a la cuadrilla a corregir
                    TareaTicket.objects.create(
                        ticket=ticket_rechazar, 
                        descripcion=f"⚠️ CORRECCIÓN: {nota_rechazo}"
                    )
                    
                    # 2. Regresamos el estatus a "En Proceso" y recalculamos porcentaje
                    ticket_rechazar.status = 'En Proceso'
                    total_t = ticket_rechazar.tareas.count()
                    hechas_t = ticket_rechazar.tareas.filter(completada=True).count()
                    ticket_rechazar.porcentaje_avance = int((hechas_t / total_t) * 100)
                    
                    nota_previa = ticket_rechazar.observaciones if ticket_rechazar.observaciones else ''
                    ticket_rechazar.observaciones = f"{nota_previa}\n\n[SISTEMA]: 🔴 Trámite devuelto por Admin con observaciones."
                    
                    # 3. Guardamos la evidencia en el ticket si adjuntó una
                    if evidencia:
                        ticket_rechazar.evidencia = evidencia
                        
                    ticket_rechazar.save()
                except TicketAyuda.DoesNotExist:
                    pass
                return redirect('inicio')

            # ESCENARIO B: REASIGNACIÓN DE DIRECTOR (Lógica que ya tenías)
            else:
                nuevo_agente_id = request.POST.get('nuevo_agente')
                try:
                    ticket_reasignar = TicketAyuda.objects.get(folio=folio_ticket)
                    if nuevo_agente_id:
                        nuevo_agente = User.objects.get(id=nuevo_agente_id)
                        ticket_reasignar.director_asignado = nuevo_agente
                        ticket_reasignar.agente_asignado = nuevo_agente 
                    else:
                        ticket_reasignar.director_asignado = None 
                        ticket_reasignar.agente_asignado = None
                        
                    nota_previa = ticket_reasignar.observaciones if ticket_reasignar.observaciones else ''
                    ticket_reasignar.observaciones = f"{nota_previa}\n\n[SISTEMA]: Flujo reasignado por el Administrador el {timezone.now().strftime('%d/%m/%Y')}."
                    ticket_reasignar.save()
                except (TicketAyuda.DoesNotExist, User.DoesNotExist):
                    pass
                return redirect('inicio')

    # --- LÓGICA DE FILTRADO Y LECTURA (GET) ---
    tickets = TicketAyuda.objects.all()
    q = request.GET.get('q', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    colonia_id = request.GET.get('colonia_id', '')
    direccion_id = request.GET.get('direccion_id', '') 

    if q: tickets = tickets.filter(Q(folio__icontains=q) | Q(nombre__icontains=q) | Q(email__icontains=q) | Q(apellido_paterno__icontains=q) | Q(apellido_materno__icontains=q) | Q(asunto__icontains=q) | Q(notas__icontains=q) | Q(calle__icontains=q))
    if fecha_inicio: tickets = tickets.filter(fecha__gte=fecha_inicio)
    if fecha_fin: tickets = tickets.filter(fecha__lte=fecha_fin)
    if colonia_id: tickets = tickets.filter(colonia_id=colonia_id)
    if direccion_id: tickets = tickets.filter(direccion_id=direccion_id)

    # KPIs
    total_tickets = tickets.count()
    tickets_nuevos = tickets.filter(status='Nuevo').count()
    tickets_validacion = tickets.filter(status='En Validación').count()
    tickets_proceso = tickets.filter(status='En Proceso').count()
    tickets_resueltos = tickets.filter(status='Resuelto').count()

    tickets_por_direccion = tickets.values('direccion__nombre_direccion').annotate(total=Count('folio')).order_by('-total')
    nombres_direcciones = [item['direccion__nombre_direccion'] for item in tickets_por_direccion if item['direccion__nombre_direccion']]
    totales_direcciones = [item['total'] for item in tickets_por_direccion if item['direccion__nombre_direccion']]

    top_asuntos = tickets.values('asunto').annotate(total=Count('folio')).order_by('-total')[:5]

    # PREPARACIÓN DE DATOS PARA EL MODAL (JSON)
    tickets_data = []
    hoy = timezone.now().date()
    for p in tickets:
        tareas_list = []
        for t in p.tareas.all().order_by('fecha_creacion'):
            tiempo = "Pendiente"
            if t.completada and t.fecha_completada:
                dias = (t.fecha_completada.date() - t.fecha_creacion.date()).days
                tiempo = "Mismo día" if dias == 0 else f"{dias} día(s)"
            
            tareas_list.append({
                'id': t.id,
                'descripcion': t.descripcion,
                'completada': t.completada,
                'ejecutor': t.ejecutor.username if t.ejecutor else '',
                'evidencia_url': t.evidencia_tarea.url if t.evidencia_tarea else '',
                'tiempo': tiempo
            })

        tickets_data.append({
            'folio': p.folio, 'lat': p.latitud if p.latitud else 'None', 'lng': p.longitud if p.longitud else 'None',
            'status': p.status, 'asunto': p.asunto, 'nombre': p.nombre,
            'email': p.email, 
            'nombre': p.nombre_completo,
            'colonia': p.colonia.nombre_colonia if p.colonia else 'N/A', 
            'direccion': p.direccion.nombre_direccion if p.direccion else 'N/A',
            'fecha': p.fecha.strftime('%d/%m/%Y'),
            'dias_abierto': (hoy - p.fecha).days,
            'notas': p.notas if p.notas else 'Sin detalles extra',
            'porcentaje': p.porcentaje_avance,
            'observaciones': p.observaciones if p.observaciones else '',
            'director': p.director_asignado.username if p.director_asignado else 'Sin asignar',
            'subdirector': p.subdirector_asignado.username if p.subdirector_asignado else 'Sin asignar',
            'coordinador': p.coordinador_asignado.username if p.coordinador_asignado else 'Sin asignar',
            'tareas': tareas_list,
            'gestor': str(p.gestor) if p.gestor else 'Ciudadano Directo',
        })

    if request.GET.get('ajax') == '1':
        return JsonResponse({
            'total_tickets': total_tickets,
            'tickets_nuevos': tickets_nuevos,
            'tickets_proceso': tickets_proceso,
            'tickets_validacion': tickets_validacion,
            'tickets_resueltos': tickets_resueltos,
            'tickets_json': tickets_data
        })

    contexto = {
        'total_tickets': total_tickets, 'tickets_nuevos': tickets_nuevos,
        'tickets_proceso': tickets_proceso, 'tickets_resueltos': tickets_resueltos,
        'tickets_validacion': tickets_validacion,
        'nombres_direcciones': nombres_direcciones, 'totales_direcciones': totales_direcciones,
        'top_asuntos': top_asuntos, 'tickets_json': json.dumps(tickets_data),
        'ultimos_tickets': tickets.order_by('-fecha')[:100], 
        'colonias': CatColonia.objects.all().order_by('nombre_colonia'), 
        'direcciones': CatDireccion.objects.all().order_by('nombre_direccion'),
        'f_q': q, 'f_fecha_inicio': fecha_inicio, 'f_fecha_fin': fecha_fin, 
        'f_colonia_id': int(colonia_id) if (colonia_id and colonia_id.isdigit()) else '',
        'f_direccion_id': int(direccion_id) if (direccion_id and direccion_id.isdigit()) else '',
        'agentes_disponibles': User.objects.filter(perfilagente__rol='Director').select_related('perfilagente__direccion_asignada')
    }
    return render(request, 'tickets/inicio.html', contexto)



@login_required(login_url='/')
def crear_ticket(request):
    if request.method == 'POST':
        formulario = TicketForm(request.POST)
        if formulario.is_valid():
            ticket = formulario.save(commit=False)
            if ticket.direccion:
                director_area = User.objects.filter(perfilagente__direccion_asignada=ticket.direccion, perfilagente__rol='Director').first()
                if director_area:
                    ticket.director_asignado = director_area
                else:
                    agentes_area = User.objects.filter(perfilagente__direccion_asignada=ticket.direccion)
                    if agentes_area.exists():
                        agentes_ordenados = agentes_area.annotate(carga_trabajo=Count('mis_tickets', filter=~Q(mis_tickets__status='Resuelto'))).order_by('carga_trabajo')
                        ticket.agente_asignado = agentes_ordenados.first()
            ticket.save()
            return redirect('inicio')
    else:
        formulario = TicketForm()
    return render(request, 'tickets/crear_ticket.html', {'formulario': formulario})

@login_required(login_url='/')
def panel_agente(request):
    usuario_actual = request.user

    try:
        rol_usuario = usuario_actual.perfilagente.rol
        area_usuario = usuario_actual.perfilagente.direccion_asignada
    except:
        rol_usuario = 'Coordinador' 
        area_usuario = None

    if request.method == 'POST':
        folio_ticket = request.POST.get('folio_ticket')
        action_4d = request.POST.get('action_4d')
        
        try:
            ticket = TicketAyuda.objects.get(
                Q(folio=folio_ticket) & (
                    Q(agente_asignado=usuario_actual) | 
                    Q(director_asignado=usuario_actual) | 
                    Q(subdirector_asignado=usuario_actual) | 
                    Q(coordinador_asignado=usuario_actual)
                )
            )

            if action_4d == 'director_plan':
                tareas_nuevas = request.POST.get('tareas_list', '') 
                subdirector_id = request.POST.get('subdirector_id')
                if tareas_nuevas:
                    for desc in tareas_nuevas.split('|'):
                        if desc.strip():
                            TareaTicket.objects.create(ticket=ticket, descripcion=desc.strip())
                if subdirector_id:
                    ticket.subdirector_asignado_id = subdirector_id
                    ticket.status = 'En Proceso'
                ticket.save()

            elif action_4d == 'subdirector_turnar':
                coordinador_id = request.POST.get('coordinador_id')
                if coordinador_id:
                    ticket.coordinador_asignado_id = coordinador_id
                    ticket.save()
            
            elif action_4d == 'aprobar_ticket' and rol_usuario == 'Director':
                ticket.status = 'Resuelto'
                ticket.porcentaje_avance = 100
                nota_previa = ticket.observaciones if ticket.observaciones else ''
                ticket.observaciones = f"{nota_previa}\n\n[SISTEMA]: 🟢 Ticket validado y cerrado por la Dirección."
                ticket.save()

            elif action_4d == 'rechazar_ticket' and rol_usuario == 'Director':
                nota_rechazo = request.POST.get('notas_agente', 'Revisión requerida')
                evidencia = request.FILES.get('evidencia_tarea')
                
                TareaTicket.objects.create(
                    ticket=ticket, 
                    descripcion=f"⚠️ CORRECCIÓN: {nota_rechazo}"
                )
                
                ticket.status = 'En Proceso'
                total_t = ticket.tareas.count()
                hechas_t = ticket.tareas.filter(completada=True).count()
                ticket.porcentaje_avance = int((hechas_t / total_t) * 100)
                
                nota_previa = ticket.observaciones if ticket.observaciones else ''
                ticket.observaciones = f"{nota_previa}\n\n[SISTEMA]: 🔴 Trámite devuelto por la Dirección."
                if evidencia:
                    ticket.evidencia = evidencia
                ticket.save()

            elif action_4d == 'completar_tarea':
                tarea_id = request.POST.get('tarea_id')
                evidencia = request.FILES.get('evidencia_tarea')
                nota_texto = request.POST.get('notas_agente', '')
                
                if tarea_id:
                    tarea = TareaTicket.objects.get(id=tarea_id)
                    tarea.completada = True
                    tarea.ejecutor = usuario_actual
                    tarea.fecha_completada = timezone.now()
                    if evidencia:
                        tarea.evidencia_tarea = evidencia
                    tarea.save()
                    
                    if nota_texto:
                        nota_previa = ticket.observaciones if ticket.observaciones else ''
                        ticket.observaciones = f"{nota_previa}\n✔️ [{tarea.descripcion}] - Nota de {usuario_actual.username}: {nota_texto}"
                    
                    total_tareas = ticket.tareas.count()
                    tareas_hechas = ticket.tareas.filter(completada=True).count()
                    if total_tareas > 0:
                        ticket.porcentaje_avance = int((tareas_hechas / total_tareas) * 100)
                        # Si llegan al 100%, lo bajamos al 95% y lo mandamos a validación
                        if ticket.porcentaje_avance == 100:
                            ticket.porcentaje_avance = 95
                            ticket.status = 'En Validación'
                    ticket.save()

            elif not action_4d:
                nuevo_status = request.POST.get('status')
                nuevo_porcentaje = request.POST.get('porcentaje')
                nuevas_notas = request.POST.get('notas_agente')
                archivo_evidencia = request.FILES.get('evidencia')
                if nuevo_status: ticket.status = nuevo_status
                if nuevo_porcentaje: ticket.porcentaje_avance = nuevo_porcentaje
                if nuevas_notas: ticket.notas_agente = nuevas_notas
                if archivo_evidencia: ticket.evidencia = archivo_evidencia
                if int(nuevo_porcentaje) == 100: ticket.status = 'Resuelto'
                ticket.save()

        except TicketAyuda.DoesNotExist:
            pass
        
        if request.POST.get('ajax_post') == '1':
            return JsonResponse({'status': 'ok'})
            
        return redirect('panel_agente')


    q = request.GET.get('q', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')
    colonia_id = request.GET.get('colonia_id', '')

    mis_tickets = TicketAyuda.objects.filter(
        Q(agente_asignado=usuario_actual) |
        Q(director_asignado=usuario_actual) |
        Q(subdirector_asignado=usuario_actual) |
        Q(coordinador_asignado=usuario_actual)
    ).distinct()

    if q: mis_tickets = mis_tickets.filter(Q(folio__icontains=q) | Q(nombre__icontains=q) | Q(email__icontains=q) | Q(apellido_paterno__icontains=q) | Q(apellido_materno__icontains=q) | Q(asunto__icontains=q) | Q(calle__icontains=q))
    if fecha_inicio: mis_tickets = mis_tickets.filter(fecha__gte=fecha_inicio)
    if fecha_fin: mis_tickets = mis_tickets.filter(fecha__lte=fecha_fin)
    if colonia_id: mis_tickets = mis_tickets.filter(colonia_id=colonia_id)

    puntos_data = []
    hoy = timezone.now().date()
    
    for p in mis_tickets: 
        if p.latitud and p.longitud:
            tareas_list = []
            for t in p.tareas.all().order_by('fecha_creacion'):
                tareas_list.append({
                    'id': t.id,
                    'descripcion': t.descripcion,
                    'completada': t.completada,
                    'ejecutor': t.ejecutor.username if t.ejecutor else '',
                    'evidencia_url': t.evidencia_tarea.url if t.evidencia_tarea else ''
                })

            puntos_data.append({
                'folio': p.folio, 'lat': float(p.latitud), 'lng': float(p.longitud),
                'status': p.status, 'asunto': p.asunto, 'nombre': p.nombre,
                'nombre': p.nombre_completo,
                'email': p.email,
                'fecha': p.fecha.strftime('%d/%m/%Y'),
                'colonia': p.colonia.nombre_colonia if p.colonia else 'N/A',
                'direccion': p.direccion.nombre_direccion if p.direccion else 'N/A',
                'dias_abierto': (hoy - p.fecha).days,
                'notas': p.notas if p.notas else 'Sin notas ciudadanas',
                'porcentaje': p.porcentaje_avance,
                'notas_agente': p.observaciones if p.observaciones else '', 
                'evidencia_url': p.evidencia.url if p.evidencia else '',
                'director': p.director_asignado.username if p.director_asignado else 'Sin asignar',
                'subdirector': p.subdirector_asignado.username if p.subdirector_asignado else 'Sin asignar',
                'coordinador': p.coordinador_asignado.username if p.coordinador_asignado else 'Sin asignar',
                'tareas': tareas_list,
                'gestor': str(p.gestor) if p.gestor else 'Ciudadano Directo'
            })

    if request.GET.get('ajax') == '1':
        return JsonResponse({'puntos_json': puntos_data})

    mis_tickets_activos = mis_tickets.exclude(status='Resuelto').order_by('fecha')
    mis_tickets_resueltos = mis_tickets.filter(status='Resuelto').order_by('-fecha')[:5]
    colonias = CatColonia.objects.all().order_by('nombre_colonia')

    empleados_inferiores = []
    if rol_usuario == 'Director' and area_usuario:
        empleados_inferiores = User.objects.filter(perfilagente__direccion_asignada=area_usuario, perfilagente__rol='Subdirector')
    elif rol_usuario == 'Subdirector' and area_usuario:
        empleados_inferiores = User.objects.filter(perfilagente__direccion_asignada=area_usuario, perfilagente__rol='Coordinador')

    contexto = {
        'tickets_activos': mis_tickets_activos, 'tickets_resueltos': mis_tickets_resueltos,
        'puntos_json': json.dumps(puntos_data), 'colonias': colonias,
        'f_q': q, 'f_fecha_inicio': fecha_inicio, 'f_fecha_fin': fecha_fin, 
        'f_colonia_id': int(colonia_id) if colonia_id.isdigit() else '',
        'rol_usuario': rol_usuario,
        'empleados_inferiores': empleados_inferiores
    }
    return render(request, 'tickets/panel_agente.html', contexto)