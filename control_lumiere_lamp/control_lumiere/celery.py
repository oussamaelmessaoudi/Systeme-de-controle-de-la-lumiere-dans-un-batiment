# control_lumiere/celery.py
import os
from celery import Celery

# Définir le module de paramètres Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'control_lumiere.settings')

# Créer l'application Celery
app = Celery('control_lumiere')

# Charger la configuration depuis les paramètres Django avec le préfixe CELERY
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découvrir automatiquement les tâches dans les applications Django
app.autodiscover_tasks()