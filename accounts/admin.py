from django.contrib import admin

from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from products.models import UserFavorite


class FavoriteInline(admin.StackedInline):
    model = UserFavorite
    extra = 1


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = get_user_model()
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ('username', 'email', 'Seller', 'is_superuser')

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('Seller',)}),
    )
    inlines = [
        FavoriteInline,
    ]




