from django.urls import path

from .views import (ProductListView, ProductDetailView, CommentCreateView,  FavoritesView, favorite_add_view,)
app_name = 'product'

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('comment/<int:pk>/', CommentCreateView.as_view(), name='product_comment'),
    path('favorites/', FavoritesView.as_view(), name='favorites'),
    path('<int:pk>/favorites_add/', favorite_add_view, name='favorite_add'),

]
