from django.db import models
from django.utils import timezone
from datetime import timedelta

# Tabla Avisos

class Aviso(models.Model):
    id_aviso = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200, verbose_name='Título del aviso')
    descripcion = models.TextField(verbose_name='Descripción o contenido del aviso')
    fecha_publicacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de publicación')

    def __str__(self):
        return self.titulo

# Tabla Noticias
    
class Noticia(models.Model):
    id_noticia = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fotografia = models.ImageField(upload_to='noticias/', blank=True, null=True)

    def __str__(self):
        return self.titulo

# Tabla Colaboradores
    
class Colaborador(models.Model):  
    id_colaborador = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fotografia = models.ImageField(upload_to='colaboradores/', blank=True, null=True)
    
    class Meta:
        db_table = 'myapp_colaborador'
    
    def __str__(self):
        return self.nombre
    
# Tabla Contactos

class Contactos(models.Model):
    id_contactos = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    numero = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, null=True)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_envio']
    
    def __str__(self):                               
        return self.nombre
    
    @classmethod
    def limpiar_antiguos(cls, dias=30):
        """
        Elimina automáticamente los registros de contactos más antiguos de 30 días
        
        Args:
            dias (int): Número de días a mantener (por defecto 30)
        
        Returns:
            tuple: (número de registros eliminados, diccionario con detalles)
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        contactos_antiguos = cls.objects.filter(fecha_envio__lt=fecha_limite)
        cantidad = contactos_antiguos.count()
        
        if cantidad > 0:
            contactos_antiguos.delete()
        
        return cantidad

