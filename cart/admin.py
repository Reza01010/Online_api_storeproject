from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.


class CartItemInline(admin.StackedInline):
    model = CartItem
    fields = ['cart', 'product', 'quantity', ]
    extra = 1


# admin.site.register(Order)
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at',
                    'updated_at', ]

    inlines = [
        CartItemInline,
    ]


# admin.site.register(OrderItem)
@admin.register(CartItem)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', ]
