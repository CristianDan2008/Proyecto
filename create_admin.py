import os
import django
from django.contrib.auth import get_user_model

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'misite.settings')
django.setup()

User = get_user_model()
username = 'admin' # O el nombre que prefieras
email = 'cristiandanielsanchez339@gmail.com'
password = '1234567890' # Usa una contraseña fuerte

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superusuario '{username}' creado exitosamente.")
else:
    print(f"El superusuario '{username}' ya existe. Saltando paso.")
