from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from django.shortcuts import get_object_or_404
from products.serializers import OrderSerializer_e
from cart.cart import Cart
from orders.models import OrderItem
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication


class OrderCreateView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def post(self, request):
        cart = Cart(request)
        if len(cart) == 0:
            return Response({'message': 'You cannot proceed to checkout page because your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
        order_form = OrderSerializer_e(data=request.data)
        if order_form.is_valid():
            order_obj = order_form.save(commit=False)
            order_obj.user = request.user
            order_obj.save()
            for item in cart:
                product = item['product_obj']
                OrderItem.objects.create(
                    order=order_obj,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price
                )
            cart.clear()
            if not request.user.first_name:
                request.user.first_name = order_obj.first_name
            if not request.user.last_name:
                request.user.last_name = order_obj.last_name
            request.user.save()
            request.session['order_id'] = order_obj.id
            return redirect('payment:payment_process_sandbox')
        else:
            return Response(order_form.errors, status=status.HTTP_400_BAD_REQUEST)


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