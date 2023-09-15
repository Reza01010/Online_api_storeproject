from django.db import models

from django.db import models
from django.utils import timezone
from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from ckeditor.fields import RichTextField


class Product(models.Model):
    title = models.CharField(_('title'), max_length=100)
    description = RichTextField(_('descript'))
    short_description = models.TextField(_('short_descript'), blank=True)
    price = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    image = models.ImageField(_('product Image'), upload_to='product/product_cover', blank=True)

    datetime_created = models.DateTimeField(_('datetime_created'), default=timezone.now)
    datetime_moified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product:product_detail', args=[self.pk])


class ActiveCommentManager(models.Manager):
    def get_queryset(self):
        return super(ActiveCommentManager, self).get_queryset().filter(active=True)


class Comment(models.Model):
    PRODUCT_STARS = [
        ('1', _('very bad')),
        ('2', _('bad')),
        ('3', _('normal')),
        ('4', _('good')),
        ('5', _('perfect')),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments',)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,
                               related_name='comments', verbose_name='comment author')
    body = models.TextField(verbose_name=_('body'))
    starts = models.CharField(max_length=10, choices=PRODUCT_STARS,verbose_name=_('star'), )

    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_moified = models.DateTimeField(auto_now=True)

    active = models.BooleanField(default=True)

    # Manager
    objects = models.Manager()
    active_comment_manager = ActiveCommentManager()

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.product.id])



class UserFavorite(models.Model):
  user = models.ForeignKey(get_user_model(),blank=True, on_delete=models.CASCADE)
  product = models.ForeignKey(Product,blank=True, on_delete=models.CASCADE)


class Contact_us(models.Model):
    name = models.CharField(max_length=100,)
    email = models.EmailField()
    phone_number = models.CharField(max_length=11)
    mesej = models.TextField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,)
    created = models.DateTimeField(default=timezone.now)