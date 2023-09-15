from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    ProductSerializer,
    CommentSerializer,
    UserFavoriteSerializer,
    ContactUsSerializer,
)
from rest_framework.decorators import api_view
from .models import Product, Comment, UserFavorite, ContactUs
from rest_framework import status
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import resolve
from django.shortcuts import render
from django.views import generic
from django.shortcuts import get_object_or_404, reverse, render
from django.utils.translation import gettext as _
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
import re
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from allauth.account.forms import ChangePasswordForm
from cart.forms import Myaccountfrom
from rest_framework.response import Response
from .models import Product, Comment, UserFavorite, Contact_us
from .forms import CommentForms, ContactForms
from cart.forms import AddToCartProductForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .forms import SearchForm
from .serializers import ContactusSerializer, MyAccountSerializer
from django.http import JsonResponse
from rest_framework import serializers



class SearchView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            return Product.objects.filter(title__icontains=query) | Product.objects.filter(description__icontains=query)
        else:
            return Product.objects.none()



class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer



class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]



class FavoritesView(generics.ListAPIView):
    serializer_class = UserFavoriteSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.favorites.all()
        else:
            favorites = self.request.session.get('favorites', {})
            pk_ = [int(key) for key in favorites if re.match(r'\d+', key)]
            return Product.objects.filter(id__in=pk_)




@api_view(['POST'])
def favorite_add_view(request, pk):
    if request.user.is_authenticated:
        favorite_ = get_object_or_404(Product, pk=pk)
        if not UserFavorite.objects.filter(
            user=request.user,
            product=favorite_
        ).exists():
            UserFavorite.objects.create(
                user=request.user,
                product=favorite_
            )
            return Response({'message': 'Favorite added successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Product already in favorites.'}, status=status.HTTP_200_OK)
    else:
        favorites = request.session.get('favorites', {})
        if pk not in favorites:
            product = Product.objects.get(pk=pk)
            favorites[pk] = product.title
            request.session['favorites'] = favorites
            return Response({'message': 'Favorite added successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Product already in favorites.'}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def contact_us_view(request):
    last_comment = Contact_us.objects.filter(user=request.user).order_by('-created').first()
    if last_comment:
        remaining_time = (last_comment.created + timedelta(hours=12) - timezone.now()).total_seconds() / 3600
        ti = round(remaining_time, 2)
        t = f'Remaining time: {ti} hours'
    else:
        remaining_time = None
        ti = None
        t = None

    if last_comment and 0 <= ti:
        return Response({'message': "You can only comment every {} hours".format(t)}, status=status.HTTP_408_REQUEST_TIMEOUT)
    elif request.method == 'POST':
        form = ContactForms(request.POST)
        serializer = ContactusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message': 'OK'})
    else:
        serializer = ContactusSerializer(data=request.data)
        e = None
        if serializer:
            e = serializer.errors
        return Response(e, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def my_account_view(request):
    form = ChangePasswordForm()
    acco_form = Myaccountfrom()
    if request.method == 'POST':
        acco_form = Myaccountfrom(request.POST)
        if acco_form.is_valid():
            if acco_form.cleaned_data['firstname']:
                request.user.first_name = acco_form.cleaned_data['firstname']
            if acco_form.cleaned_data['lastname']:
                request.user.last_name = acco_form.cleaned_data['lastname']
            if acco_form.cleaned_data['email']:
                request.user.email = acco_form.cleaned_data['email']
            if acco_form.cleaned_data['username']:
                request.user.username = acco_form.cleaned_data['username']
            request.user.save()
    if request.user.is_authenticated:
        favorite_ = request.user.favorites.all()
    o = Order.objects.filter(user=request.user)

    return render(request, 'my_account.html',
                  context={'list_fe': favorite_, 'order': o, 'form': form, "acco_form": acco_form})



@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def my_account_view(request):
    if request.method == 'POST':
        acco_form = MyAccountSerializer(data=request.data)
        if acco_form.is_valid():
            acco_formv = acco_form.validated_data
            if acco_formv.get('firstname'):
                request.user.first_name = acco_formv['firstname']
            if acco_formv.get('lastname'):
                request.user.last_name = acco_formv['lastname']
            if acco_formv.get('email'):
                request.user.email = acco_formv['email']
            if acco_formv.get('username'):
                request.user.username = acco_formv['username']
            request.user.save()

        return Response(acco_form.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        favorite_ = request.user.favorites.all()
        serializerfa = serializers.serialize(favorite_, many=True)
        serialized_data_fa = serializerfa.data
        o = Order.objects.filter(user=request.user)
        serializero = serializers.serialize(o, many=True)
        serialized_data_o = serializero.data
    # return JsonResponse((serialized_data_fa,serialized_data_o), safe=False, status=status.HTTP_200_OK)









