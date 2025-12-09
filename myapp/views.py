"""
VIEWS - SEMARTEC Portal de Avisos
Gestiona avisos, noticias, colaboradores y generación de PDF
"""

# ==================== IMPORTACIONES ====================
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime, timedelta
from django.utils import timezone

# Modelos
from .models import Aviso, Noticia, Colaborador, Contactos

# ReportLab para PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT


# ==================== UTILIDADES ====================

def _check_staff_permission(request, redirect_view='inicio'):
    """Valida que el usuario sea staff (administrador)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder aquí')
        return redirect(redirect_view)
    return None


def _truncate_text(text, max_length=100):
    """Trunca texto a un máximo de caracteres, cortando en espacios"""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + "..."


def _limit_words(text, max_words=15):
    """Limita el texto a un número máximo de palabras"""
    words = text.split()
    if len(words) <= max_words:
        return text
    return ' '.join(words[:max_words]) + "..."


# ==================== AUTENTICACIÓN ====================

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vista de login personalizada"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('inicio-admin' if user.is_staff else 'inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'login.html')


@login_required(login_url='login')
def logout_view(request):
    """Cierra la sesión del usuario"""
    logout(request)
    return redirect('inicio')


# ==================== VISTAS PÚBLICAS ====================

def inicio(request):
    """Página de inicio pública con últimos elementos"""
    ctx = {
        'avisos': Aviso.objects.order_by('-fecha_publicacion')[:4],
        'noticias': Noticia.objects.order_by('-fecha_publicacion')[:4],
        'colaboradores': Colaborador.objects.all()[:4],
    }
    return render(request, 'inicio.html', ctx)


def avisos(request):
    """Listado de avisos públicos"""
    ctx = {'avisos': Aviso.objects.order_by('-fecha_publicacion')}
    return render(request, 'avisos.html', ctx)


class AvisoDetailView(DetailView):
    model = Aviso
    template_name = 'aviso_detail.html'
    context_object_name = 'aviso'
    pk_url_kwarg = 'pk'


def noticias(request):
    """Listado de noticias públicas"""
    ctx = {'noticias': Noticia.objects.all().order_by('-fecha_publicacion')}
    return render(request, 'noticias.html', ctx)


class NoticiaDetailView(DetailView):
    model = Noticia
    template_name = 'noticia_detail.html'
    context_object_name = 'noticia'
    pk_url_kwarg = 'pk'


def colaboradores(request):
    """Listado de colaboradores públicos"""
    ctx = {'colaboradores': Colaborador.objects.all()}
    return render(request, 'colaboradores.html', ctx)


class ColaboradorDetailView(DetailView):
    model = Colaborador
    template_name = 'colaborador_detail.html'
    context_object_name = 'colaborador'
    pk_url_kwarg = 'pk'


# ==================== VISTAS DE ADMINISTRACIÓN ====================

@login_required(login_url='login')
def inicio_admin(request):
    """Panel inicial del administrador"""
    check = _check_staff_permission(request)
    if check:
        return check
    return render(request, 'InicioAdmin.html')


@login_required(login_url='login')
def admin_avisos(request):
    """Panel de administración de avisos"""
    check = _check_staff_permission(request)
    if check:
        return check
    
    ctx = {
        'total_avisos': Aviso.objects.count(),
        'avisos': Aviso.objects.all().order_by('-fecha_publicacion'),
    }
    return render(request, 'admin_avisos.html', ctx)


@login_required(login_url='login')
def admin_noticias(request):
    """Panel de administración de noticias"""
    check = _check_staff_permission(request)
    if check:
        return check
    
    ctx = {
        'total_noticias': Noticia.objects.count(),
        'noticias': Noticia.objects.all().order_by('-fecha_publicacion'),
    }
    return render(request, 'admin_noticias.html', ctx)


@login_required(login_url='login')
def admin_colaboradores(request):
    """Panel de administración de colaboradores"""
    check = _check_staff_permission(request)
    if check:
        return check
    
    ctx = {
        'total_colaboradores': Colaborador.objects.count(),
        'colaboradores': Colaborador.objects.all(),
    }
    return render(request, 'admin_colaboradores.html', ctx)


@login_required(login_url='login')
def admin_contactos(request):
    """Panel de administración de contactos"""
    check = _check_staff_permission(request)
    if check:
        return check
    
    # Información de limpieza automática
    fecha_limite = timezone.now() - timedelta(days=30)
    contactos_antiguos = Contactos.objects.filter(fecha_envio__lt=fecha_limite)
    cantidad_por_eliminar = contactos_antiguos.count()
    
    ctx = {
        'total_contactos': Contactos.objects.count(),
        'contactos': Contactos.objects.all(),
        'contactos_por_eliminar': cantidad_por_eliminar,
        'fecha_limite': fecha_limite,
    }
    return render(request, 'admin_contactos.html', ctx)


# ==================== CLASES BASE ====================

class BaseStaffDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Clase base para vistas de eliminación con validación de staff"""
    login_url = 'login'
    error_message = 'No tienes permisos para eliminar este elemento'
    
    def test_func(self):
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, self.error_message)
        return redirect(self.success_url)


# ==================== CRUD - AVISOS ====================

class AvisoCreateView(LoginRequiredMixin, CreateView):
    model = Aviso
    fields = ['titulo', 'descripcion']
    template_name = 'aviso_form.html'
    success_url = reverse_lazy('admin-avisos')
    login_url = 'login'


class AvisoUpdateView(LoginRequiredMixin, UpdateView):
    model = Aviso
    fields = ['titulo', 'descripcion']
    template_name = 'aviso_form.html'
    success_url = reverse_lazy('admin-avisos')
    login_url = 'login'


class AvisoDeleteView(BaseStaffDeleteView):
    model = Aviso
    template_name = 'avElim.html'
    success_url = reverse_lazy('admin-avisos')
    error_message = 'No tienes permisos para eliminar avisos'


# ==================== CRUD - NOTICIAS ====================

class NoticiaCreateView(LoginRequiredMixin, CreateView):
    model = Noticia
    fields = ['titulo', 'descripcion', 'fotografia']
    template_name = 'noticia_form.html'
    success_url = reverse_lazy('admin-noticias')
    login_url = 'login'


class NoticiaUpdateView(LoginRequiredMixin, UpdateView):
    model = Noticia
    fields = ['titulo', 'descripcion', 'fotografia']
    template_name = 'noticia_form.html'
    success_url = reverse_lazy('admin-noticias')
    login_url = 'login'


class NoticiaDeleteView(BaseStaffDeleteView):
    model = Noticia
    template_name = 'noticia_elim.html'
    success_url = reverse_lazy('admin-noticias')
    error_message = 'No tienes permisos para eliminar noticias'


# ==================== CRUD - COLABORADORES ====================

class ColaboradorCreateView(LoginRequiredMixin, CreateView):
    model = Colaborador
    fields = ['nombre', 'descripcion', 'fotografia']
    template_name = 'colaboradores_form.html'
    success_url = reverse_lazy('admin-colaboradores')
    login_url = 'login'


class ColaboradorUpdateView(LoginRequiredMixin, UpdateView):
    model = Colaborador
    fields = ['nombre', 'descripcion', 'fotografia']
    template_name = 'colaboradores_form.html'
    success_url = reverse_lazy('admin-colaboradores')
    login_url = 'login'


class ColaboradorDeleteView(BaseStaffDeleteView):
    model = Colaborador
    template_name = 'colaboradores_elim.html'
    success_url = reverse_lazy('admin-colaboradores')
    error_message = 'No tienes permisos para eliminar colaboradores'


# ==================== CRUD - CONTACTOS ====================

# ==================== CREAR SOLO PARA USUARIOS ====================

class ContactosCreateView(CreateView):
    model = Contactos
    fields = ['nombre', 'numero', 'email', 'mensaje']
    template_name = 'contactos_form.html'
    success_url = reverse_lazy('inicio')


class ContactosUpdateView(LoginRequiredMixin, UpdateView):
    model = Contactos
    fields = ['nombre', 'numero', 'email', 'mensaje']
    template_name = 'contactos_form.html'
    success_url = reverse_lazy('admin-contactos')
    login_url = 'login'


class ContactosDetailView(LoginRequiredMixin, DetailView):
    model = Contactos
    template_name = 'contactos_detail.html'
    context_object_name = 'contacto'
    login_url = 'login'
    
    def test_func(self):
        """Solo staff puede ver los detalles"""
        return self.request.user.is_staff


class ContactosDeleteView(BaseStaffDeleteView):
    model = Contactos
    template_name = 'contactos_elim.html'
    success_url = reverse_lazy('admin-contactos')
    error_message = 'No tienes permisos para eliminar contactos'


# ==================== GENERADOR DE PDF ====================

@login_required(login_url='login')
def generar_boletin_pdf(request):
    """Genera un boletín informativo en PDF con avisos, noticias y colaboradores"""
    check = _check_staff_permission(request, 'inicio')
    if check:
        return check
    
    # Crear documento PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=0.4*inch, leftMargin=0.4*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#008080'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#008080'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#008080'),
        borderWidth=1,
        borderPadding=5
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    # Estilo para celdas de tabla - ajuste automático de ancho
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['BodyText'],
        fontSize=6.5,
        alignment=TA_LEFT,
        spaceAfter=0,
        leading=8,
        wordWrap='CJK'
    )
    
    # Título
    story.append(Paragraph("BOLETÍN INFORMATIVO SEMARTEC", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Fecha
    fecha_actual = datetime.now().strftime("%d de %B de %Y - %H:%M")
    story.append(Paragraph(f"<b>Fecha:</b> {fecha_actual}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Estilos de tabla - con altura fija de fila
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#008080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('ROWHEIGHTS', (0, 0), (-1, -1), 20),
    ]
    
    # Sección AVISOS
    story.append(Paragraph("📢 AVISOS", section_style))
    avisos = Aviso.objects.all().order_by('-fecha_publicacion')[:10]
    
    if avisos.exists():
        avisos_data = [['Título', 'Descripción', 'Fecha']]
        for aviso in avisos:
            fecha_str = aviso.fecha_publicacion.strftime("%d/%m/%Y") if aviso.fecha_publicacion else "N/A"
            # Truncar fuertemente a 60 caracteres
            titulo = _truncate_text(aviso.titulo, 20)
            desc = _truncate_text(aviso.descripcion, 40)
            avisos_data.append([titulo, desc, fecha_str])
        
        table = Table(avisos_data, colWidths=[1.0*inch, 3.0*inch, 0.9*inch])
        table.setStyle(TableStyle(table_style))
        story.append(table)
    else:
        story.append(Paragraph("<i>No hay avisos registrados</i>", body_style))
    
    story.append(Spacer(1, 0.25*inch))
    
    # Sección NOTICIAS
    story.append(Paragraph("📰 NOTICIAS", section_style))
    noticias = Noticia.objects.all().order_by('-fecha_publicacion')[:10]
    
    if noticias.exists():
        noticias_data = [['Título', 'Descripción', 'Fecha']]
        for noticia in noticias:
            fecha_str = noticia.fecha_publicacion.strftime("%d/%m/%Y") if noticia.fecha_publicacion else "N/A"
            titulo = _truncate_text(noticia.titulo, 20)
            desc = _truncate_text(noticia.descripcion, 40)
            noticias_data.append([titulo, desc, fecha_str])
        
        table = Table(noticias_data, colWidths=[1.0*inch, 3.0*inch, 0.9*inch])
        table.setStyle(TableStyle(table_style))
        story.append(table)
    else:
        story.append(Paragraph("<i>No hay noticias registradas</i>", body_style))
    
    story.append(Spacer(1, 0.25*inch))
    
    # Sección COLABORADORES
    story.append(Paragraph("👥 EQUIPO DE COLABORADORES", section_style))
    colaboradores = Colaborador.objects.all()
    
    if colaboradores.exists():
        colabs_data = [['Nombre', 'Descripción']]
        for colab in colaboradores:
            nombre = _truncate_text(colab.nombre, 20)
            desc = _truncate_text(colab.descripcion, 40)
            colabs_data.append([nombre, desc])
        
        table = Table(colabs_data, colWidths=[1.3*inch, 4.6*inch])
        table.setStyle(TableStyle(table_style))
        story.append(table)
    else:
        story.append(Paragraph("<i>No hay colaboradores registrados</i>", body_style))
    
    # Pie de página
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("_" * 80, body_style))
    story.append(Paragraph(
        "<i>Este boletín fue generado automáticamente por el sistema SEMARTEC. "
        "Contiene información confidencial de la organización.</i>",
        body_style
    ))
    
    # Construir PDF
    doc.build(story)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Boletin_SEMARTEC_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response
    # Pie de página
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph("_" * 80, body_style))
    story.append(Paragraph(
        "<i>Este boletín fue generado automáticamente por el sistema SEMARTEC. "
        "Contiene información confidencial de la organización.</i>",
        body_style
    ))
    
    # Construir PDF
    doc.build(story)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Boletin_SEMARTEC_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response


@login_required(login_url='login')
def generar_contactos_pdf(request):
    """Genera un PDF con la relación de todos los contactos en formato tabla"""
    check = _check_staff_permission(request, 'inicio')
    if check:
        return check
    
    # Crear documento PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=0.4*inch, leftMargin=0.4*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#008080'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=8
    )
    
    # Título
    story.append(Paragraph("RELACIÓN DE CONTACTOS", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Fecha
    fecha_actual = datetime.now().strftime("%d de %B de %Y - %H:%M")
    story.append(Paragraph(f"<b>Fecha:</b> {fecha_actual}", body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Estilos de tabla - mejorado para evitar que texto sobrepase celdas
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#008080')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]
    
    # Obtener todos los contactos
    contactos = Contactos.objects.all().order_by('-fecha_envio')
    
    if contactos.exists():
        # Preparar datos para la tabla
        contactos_data = [['Nombre', 'Número', 'Email', 'Fecha']]
        
        for contacto in contactos:
            fecha_str = contacto.fecha_envio.strftime("%d/%m/%Y %H:%M") if contacto.fecha_envio else "N/A"
            
            contactos_data.append([
                _truncate_text(contacto.nombre, 20),
                _truncate_text(contacto.numero, 15),
                _truncate_text(contacto.email, 35),
                fecha_str
            ])
        
        # Crear tabla con ancho dinámico
        table = Table(contactos_data, colWidths=[2*inch, 1.0*inch, 2.5*inch, 1*inch])
        table.setStyle(TableStyle(table_style))
        story.append(table)
        
        # Información de resumen
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(f"<b>Total de contactos:</b> {contactos.count()}", body_style))
    else:
        story.append(Paragraph("<i>No hay contactos registrados</i>", body_style))
    
    # Pie de página
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph("_" * 80, body_style))
    story.append(Paragraph(
        "<i>Este documento fue generado automáticamente por el sistema SEMARTEC. "
        "Contiene información confidencial de la organización.</i>",
        body_style
    ))
    
    # Construir PDF
    doc.build(story)
    
    # Preparar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Contactos_SEMARTEC_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response


# ==================== MANTENIMIENTO Y LIMPIEZA ====================

@login_required(login_url='login')
def limpiar_contactos_manual(request):
    """
    Vista para ejecutar limpieza manual de contactos antiguos (más de 30 días)
    Solo accesible por administradores
    """
    check = _check_staff_permission(request, 'admin-contactos')
    if check:
        return check
    
    try:
        # Ejecutar limpieza usando el método del modelo
        cantidad = Contactos.limpiar_antiguos(dias=30)
        
        if cantidad > 0:
            messages.success(
                request,
                f'✓ Se eliminaron {cantidad} registro(s) de contacto más antiguo(s) de 30 días'
            )
        else:
            messages.info(
                request,
                'No hay registros de contactos más antiguos de 30 días para eliminar'
            )
    
    except Exception as e:
        messages.error(
            request,
            f'✗ Error al limpiar contactos: {str(e)}'
        )
    
    return redirect('admin-contactos')


