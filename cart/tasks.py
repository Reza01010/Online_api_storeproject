from __future__ import absolute_import, unicode_literals

from celery import shared_task
from config.celery import app
# ----
from django.contrib import messages
from django.utils.translation import gettext as _

from products.models import Product


from django.core.mail import send_mail
from django.conf import settings


@shared_task
def add__(x, y):
    print('\n"-_-"' * 20, x+y, '\n"-_-"' * 20)
    return


def add_(x, y):
    print('\n"-_-"' * 20, x+y, '\n"-_-"' * 20)
    return


@shared_task
def send_order_confirmation_email(email,text):
    subject = 'Payment Confirmation'
    message = text
    from_email = 'your_email@example.com'
    to_email = [str(email)]
    send_mail(subject, message, from_email, to_email)
