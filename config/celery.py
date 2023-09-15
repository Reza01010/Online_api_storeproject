from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
# Manually set the Django settings module
DJANGO_SETTINGS_MODULE = 'config.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', DJANGO_SETTINGS_MODULE)
# Create a Celery application
# app = Celery('config')


app = Celery('config', backend='rpc://', broker='amqp://guest:guest@rabbit:5672//')

# Load task modules from all registered Django app configs
app.autodiscover_tasks()
