import os
from django.core.wsgi import get_wsgi_application

# Vercel defaults to production if not set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'kararsizim.settings.production'))

application = get_wsgi_application()
app = application
