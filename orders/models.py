from django.db import models

from django.db import models

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# for claynt
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.CASCADE)
    is_paid = models.BooleanField(_("Is Paid"), default=False)

    first_name = models.CharField(_("First Name"), max_length=100)
    last_name = models.CharField(_("Last Name"), max_length=100)
    phone_number = models.CharField(_("Phone Number"), max_length=15)
    address = models.CharField(_("Address"), max_length=700)

    order_notes = models.CharField(_("Order Notes"), max_length=800, blank=True)

    zarinpal_authority = models.CharField(max_length=250, blank=True)
    zarinpal_ref_id = models.CharField(max_length=150, blank=True)
    zarinpal_data = models.TextField(blank=True)

    datetime_created = models.DateTimeField(_("Created"), auto_now_add=True)
    datetime_modified = models.DateTimeField(_("Modified"), auto_now=True)

    def __str__(self):
        return f'Order {self.id}'

    def get_total_price(self):
        return sum(item.quantity * item.price for item in self.items.all())
    def get_number_of_paid_orders(self, user):
        return Order.objects.filter(is_paid=False, user=user)

# for coocki
class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("Order"), on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', verbose_name=_("Product"), on_delete=models.CASCADE, related_name='order_item')
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    price = models.PositiveIntegerField(_("Price"), )

    def __str__(self):
        return f'OrderItem {self.id} : {self.product} x {self.quantity} (price : {self.price}) '


