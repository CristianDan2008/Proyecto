from django.urls import path
from . import views
from .views import (
    AvisoCreateView, AvisoUpdateView, AvisoDeleteView, AvisoDetailView,
    NoticiaCreateView, NoticiaUpdateView, NoticiaDeleteView, NoticiaDetailView,
    ColaboradorCreateView, ColaboradorUpdateView, ColaboradorDeleteView, ColaboradorDetailView,
    ContactosCreateView, ContactosUpdateView, ContactosDeleteView, ContactosDetailView
)

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # CRUD Avisos
    path('avisos/', views.avisos, name='avisos'),
    path('avisos/<int:pk>/', AvisoDetailView.as_view(), name='aviso-detalle'),
    path('avisos/crear/', AvisoCreateView.as_view(), name='aviso-crear'),
    path('avisos/<int:pk>/editar/', AvisoUpdateView.as_view(), name='aviso-editar'),
    path('avisos/<int:pk>/eliminar/', AvisoDeleteView.as_view(), name='aviso-eliminar'),
    path('admin-avisos/', views.admin_avisos, name='admin-avisos'),
    
    # CRUD Noticias
    path('noticias/', views.noticias, name='noticias'),
    path('noticias/<int:pk>/', NoticiaDetailView.as_view(), name='noticia-detalle'),
    path('noticias/crear/', NoticiaCreateView.as_view(), name='noticia-crear'),
    path('noticias/<int:pk>/editar/', NoticiaUpdateView.as_view(), name='noticia-editar'),
    path('noticias/<int:pk>/eliminar/', NoticiaDeleteView.as_view(), name='noticia-eliminar'),
    path('admin-noticias/', views.admin_noticias, name='admin-noticias'),
    
    # CRUD Colaboradores
    path('colaboradores/', views.colaboradores, name='colaboradores'),
    path('colaboradores/<int:pk>/', ColaboradorDetailView.as_view(), name='colaborador-detalle'),
    path('colaboradores/crear/', ColaboradorCreateView.as_view(), name='colaborador-crear'),
    path('colaboradores/<int:pk>/editar/', ColaboradorUpdateView.as_view(), name='colaborador-editar'),
    path('colaboradores/<int:pk>/eliminar/', ColaboradorDeleteView.as_view(), name='colaborador-eliminar'),
    path('admin-colaboradores/', views.admin_colaboradores, name='admin-colaboradores'),
    
    #CRUD Contactos
    path('contactos/crear/', ContactosCreateView.as_view(), name='contactos-crear'),
    path('contactos/<int:pk>/', ContactosDetailView.as_view(), name='contactos-detalle'),
    path('contactos/<int:pk>/editar/', ContactosUpdateView.as_view(), name='contactos-editar'),
    path('contactos/<int:pk>/eliminar/', ContactosDeleteView.as_view(), name='contactos-eliminar'),
    path('admin-contactos/', views.admin_contactos, name='admin-contactos'),
    path('admin-contactos/limpiar/', views.limpiar_contactos_manual, name='limpiar-contactos'),

    # Panel de administrador
    path('inicio-admin/', views.inicio_admin, name='inicio-admin'),

    # URL de pdf
    path('generar-pdf/', views.generar_boletin_pdf, name='generar-pdf'),
    path('generar-contactos-pdf/', views.generar_contactos_pdf, name='generar-contactos-pdf'),
]

