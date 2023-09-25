from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    ProductSerializer,
    CommentSerializer,
    UserFavoriteSerializer,
    ContactUsSerializer,
    MyAccountSerializer,
    OrderSerializer_e,
)
from rest_framework import status
from django.shortcuts import get_object_or_404
import re
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from rest_framework.response import Response
from .models import Product, Comment, UserFavorite, Contact_us
from cart.forms import AddToCartProductForm
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authentication import BasicAuthentication


class SearchView(generics.ListAPIView):
    serializer_class = ProductSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            return Product.objects.filter(title__icontains=query) | Product.objects.filter(description__icontains=query)
        else:
            return Product.objects.none()


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    http_method_names = ["get"]


class ProductDetailView(generics.RetrieveAPIView):
    authentication_classes = [BasicAuthentication]
    queryset = Product.objects.filter(active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]


class CommentCreateView(generics.CreateAPIView):
    authentication_classes = [BasicAuthentication]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]


class FavoritesView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    serializer_class = UserFavoriteSerializer
    http_method_names = ["get"]


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.favorites.all()
        else:
            favorites = self.request.session.get('favorites', {})
            pk_ = [int(key) for key in favorites if re.match(r'\d+', key)]
            return Product.objects.filter(id__in=pk_)

def geet_Product_object(pk):
    try:
        return Product.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes(BasicAuthentication)
@permission_classes([IsAuthenticated])
def favorite_add_view(request, pk):
    if request.user.is_authenticated:
        favorite_ = geet_Product_object(pk=pk)
        if not UserFavorite.objects.filter(
            user=request.user,
            product=favorite_
        ).exists():
            serializer = UserFavoriteSerializer(data={'user': request.user.id, 'product': favorite_.id})
            if serializer.is_valid():
                serializer.save()
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
@authentication_classes(BasicAuthentication)
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
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message': 'OK'})

        e = None
        if serializer:
            e = serializer.errors
        return Response(e, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST','GET'])
@authentication_classes(BasicAuthentication)
@permission_classes([IsAuthenticated])
def my_account_view(request):

    if request.method == 'POST':
        acco_form = MyAccountSerializer(data=request.data)
        if acco_form.is_valid():
            acco_formv = acco_form.validated_data
            if not request.user.first_name and acco_formv.get('firstname'):
                request.user.first_name = acco_formv['firstname']
            if not request.user.last_name and acco_formv.get('lastname'):
                request.user.last_name = acco_formv['lastname']
            if not request.user.email and acco_formv.get('email'):
                request.user.email = acco_formv['email']
            if not request.user.username and acco_formv.get('username'):
                request.user.username = acco_formv['username']
            request.user.save()
            return Response(acco_form.data, status=status.HTTP_200_OK)
        return Response(acco_form.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        favorite_ = request.user.favorites.all()
        serializerfa = serializers.serialize('json', favorite_)
        serialized_data_fa = serializerfa.data
        o = Order.objects.filter(user=request.user)
        serializero = OrderSerializer_e(o)
        serialized_data_o = serializero.data
        serializer_myaccount = MyAccountSerializer(request.user)
    return JsonResponse({'listfe': serialized_data_fa, 'order':serialized_data_o, 'myaccount': serializer_myaccount}, safe=False, status=status.HTTP_200_OK)







