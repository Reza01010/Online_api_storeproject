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
    ProductSerializer_d,
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
from rest_framework.views import APIView
import json



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
    serializer_class = ProductSerializer_d
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]


class CommentCreateView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]


    def post(self, request, pk):
        data = request.data
        try:
            product = Product.objects.get(id=int(pk))
            coment_ser = CommentSerializer(data=data)
            if coment_ser.is_valid():
                coment = coment_ser.validated_data
                if not coment['product'] == product:
                    return Response({'note': 'The id to which you sent that address must match the id of the product that is in the post data'}, status=status.HTTP_400_BAD_REQUEST)
                
                comment_ = Comment.objects.create(
                    author=request.user,
                    active=True,
                    product=coment['product'],
                    body=coment['body'],
                    starts=coment['starts'],
                )

                coment__ = CommentSerializer(comment_)

                return Response({'comment':coment__.data},status=status.HTTP_200_OK)
                
            else:
                return Response({'serializer_errors':coment_ser.errors, "serializer_error_messages":coment_ser.error_messages},status=status.HTTP_400_BAD_REQUEST)
        except:
            
            return Response(status=status.HTTP_400_BAD_REQUEST)









class FavoritesView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserFavoriteSerializer
    http_method_names = ["get"]


    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.favorites.all()
        # else:
        #     favorites = self.request.session.get('favorites', {})
        #     pk_ = [int(key) for key in favorites if re.match(r'\d+', key)]
        #     return Product.objects.filter(id__in=pk_)





@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def favorite_add_view(request, pk):
    if request.user.is_authenticated:
        try:
            obj = Product.objects.get(pk=pk)
            favorite_=obj
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

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
    # else:
    #     favorites = request.session.get('favorites', {})
    #     if pk not in favorites:
    #         product = Product.objects.get(pk=pk)
    #         favorites[pk] = product.title
    #         request.session['favorites'] = favorites
    #         return Response({'message': 'Favorite added successfully.'}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'message': 'Product already in favorites.'}, status=status.HTTP_200_OK)



@api_view(['POST'])
@authentication_classes([BasicAuthentication])
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
    if request.method == 'POST':
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            serializer_ = serializer.validated_data
            Contact_us.objects.create(
                user=request.user,
                mesej=serializer_['mesej'],
                phone_number=serializer_['phone_number'],
                email=serializer_['email'],
                name=serializer_['name'],

            )


            return Response({'message': 'OK'})

        e = None
        if serializer:
            e = serializer.errors
        return Response(e, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST','GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def my_account_view(request):

    if request.method == 'POST':
        acco_form = MyAccountSerializer(data=request.data)
        
        if acco_form.is_valid():
            acco_formv = acco_form.validated_data
            list = []
            list_n= []
            if not request.user.first_name and acco_formv.get('first_name'):
                request.user.first_name = acco_formv['first_name']
            elif acco_formv.get('first_name'):
                list.append('first_name')
            elif not request.user.first_name:
                list_n.append('first_name')
            if not request.user.last_name and acco_formv.get('last_name'):
                request.user.last_name = acco_formv['last_name']
            elif acco_formv.get('last_name'):
                list.append('last_name')
            elif not request.user.last_name:
                list_n.append('last_name')
            if not request.user.email and acco_formv.get('email'):
                request.user.email = acco_formv['email']
            elif acco_formv.get('email'):
                list.append('email')
            elif not request.user.email:
                list_n.append('email')
            if not request.user.username and acco_formv.get('username'):
                request.user.username = acco_formv['username']
            elif acco_formv.get('username'):
                list.append('username')
            elif not request.user.username:
                list_n.append('username')
            request.user.save()

            serializer_myaccount = MyAccountSerializer(request.user)
            if list_n.__len__() > 0 and list.__len__() > 0:
                return Response({"my_account": dict(serializer_myaccount.data), "note1": f"These fields are already filled  ==> [{list}] ", "note2": f"These fields are empty  ==> [{list_n}] "}, status=status.HTTP_200_OK)
            if list.__len__() > 0:
                return Response({"my_account": dict(serializer_myaccount.data), "note": f"These fields are already filled  ==> [{list}] "}, status=status.HTTP_200_OK)
            if list_n.__len__() > 0:
                return Response({"my_account": dict(serializer_myaccount.data),  "note": f"These fields are empty  ==> [{list_n}] "}, status=status.HTTP_200_OK)
            return Response(acco_form.data, status=status.HTTP_200_OK)
        return Response({'error':acco_form.errors}, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        favorite_ = request.user.favorites.all()
        serializerfa = [{'id': f.id, 'name': f.title} for f in favorite_]
        serialized_data_fa = serializerfa
        o = Order.objects.prefetch_related('items').filter(user=request.user)
        serializero = OrderSerializer_e(o, many=True)
        serialized_data_o = serializero.data
        serializer_myaccount = MyAccountSerializer(request.user)
        return Response({'listfe': serialized_data_fa, 'order':serialized_data_o, 'myaccount': serializer_myaccount.data}, status=status.HTTP_200_OK)







