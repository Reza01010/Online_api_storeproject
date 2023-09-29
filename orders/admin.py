from django.contrib import admin

from django.contrib import admin

from django.contrib import admin
# from jalali_date.admin import ModelAdminJalaliMixin

from .models import Order, OrderItem


class CommentsInline(admin.StackedInline):
    model = OrderItem
    fields = ['order', 'product', 'quantity', 'price',]
    extra = 1


# admin.site.register(Order)
@admin.register(Order)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_paid',
                    'first_name', 'last_name', 'phone_number', 'address', 'order_notes', 'datetime_created']

    inlines = [
        CommentsInline,
    ]


# admin.site.register(OrderItem)
@admin.register(OrderItem)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['order', 'product','quantity',
                    'price',]


