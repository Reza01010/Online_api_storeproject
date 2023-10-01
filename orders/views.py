from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from django.shortcuts import get_object_or_404
from products.serializers import OrderSerializer_e,OrderSerializer_e_t, OrderItemSerializer
from orders.models import OrderItem
from cart.models import Cart, CartItem
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication


class OrderCreateView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def post(self, request):
        data = request.data
        print(data, "HRTRfg4444444444444444444444444444"*5)
        # data_ = OrderSerializer_e_t(data=data)
        try:
            cart = Cart.objects.get(user=request.user.id)
            cart_item = CartItem.objects.filter(cart=cart)

            item = OrderItemSerializer(cart_item, many=True)

            order = OrderSerializer_e_t(data=data)
            print(":"*20)
            if order.is_valid():
                order.user = request.user.id
                order.is_paid = False
                order.save()

            print("---_"*90)
            
            if item.is_valid():
                print("&"*200)
                order_obj = item.save(commit=False)
                print("#" * 200)
                order_obj.save()
                print("@" * 200)
                return Response(status=status.HTTP_200_OK)
        except:
            if len(cart) == 0:
                return Response({'message': 'You cannot proceed to checkout page because your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

            if not request.user.first_name:
                request.user.first_name = order_obj.first_name
            if not request.user.last_name:
                request.user.last_name = order_obj.last_name
            request.user.save()
            request.session['order_id'] = order_obj.id
            return redirect('payment:payment_process_sandbox')
        else:
            return Response(item.errors, status=status.HTTP_400_BAD_REQUEST)








class OrderUnpaidView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request):
        user = request.user
        o = Order.get_number_of_paid_orders(user=user)
        if not o:
            return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'order_unpaid_id': o}, status=status.HTTP_200_OK)


class OrderDeleteView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["delete"]

    def geet_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        order = self.geet_object(pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderContinueView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def geet_object(self, pk):
        try:
            return Order.objects.get(pk=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk):
        order = self.geet_object(pk)
        request.session['order_id'] = pk
        return Response(status=status.HTTP_200_OK)