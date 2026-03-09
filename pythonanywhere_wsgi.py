import os
import sys

# PythonAnywhere serveringizdagi loyiha (backend) joylashgan manzil:
# Buni o'z profilingizdagi Username ga moslang
path = '/home/neoncheck/Matbuot/backend'
if path not in sys.path:
    sys.path.append(path)

# Django parametrlarini sozlash
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

# WSGI dasturini yuklash
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
