from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from django.shortcuts import get_object_or_404
from products.serializers import OrderSerializer_e
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
        try:
            cart = Cart.objects.get(user=request.user.id)
            cart_item = CartItem.objects.filter(cart=cart)
            data["items"] = [] 


            for item in cart_item:
                item_data = {
                    "product": item.product.id,
                    "quantity": item.quantity,
                    "price": item.get_total_price()
                }
                data["items"].append(item_data)



            order_form = OrderSerializer_e(data=data)
            if order_form.is_valid():
                order = order_form.validated_data
                order_obj = Order.objects.create(
        user=request.user,
        is_paid=False,
        first_name=order['first_name'],
        last_name=order['last_name'],
        phone_number=order['phone_number'],
        address=order['address'],
        order_notes=order['order_notes'],
    )
                for item in cart_item:
                    OrderItem.objects.create(
            order=order_obj,
            product=item.product,
            quantity=item.quantity,
            price=item.get_total_price(),
        )
                
            else:
                return Response({'serializer_errors':order_form.errors, "serializer_error_messages":order_form.error_messages},status=status.HTTP_400_BAD_REQUEST)
        except:
            cart = Cart.objects.get(user=request.user.id)
            cart_item = CartItem.objects.filter(cart=cart)
            if not cart:
                return Response({'message': 'You cannot proceed to the checkout page because you do not have a shopping cart'}, status=status.HTTP_400_BAD_REQUEST)
            elif not cart_item:
                return Response({'message': 'You cannot proceed to checkout page because your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.first_name:
            request.user.first_name = order_obj.first_name
        if not request.user.last_name:
            request.user.last_name = order_obj.last_name
        request.user.save()
        request.session['order_id'] = order_obj.id
        return redirect('payment:payment_process_sandbox')



class OrderUnpaidView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]

    def get(self, request):
        user = request.user
        o = Order()
        obj_ = o.get_number_of_paid_orders(user=user)
        obj=OrderSerializer_e(obj_, many=True)
        if not obj_:
            return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'order_unpaid_id': obj.data}, status=status.HTTP_200_OK)


class OrderDeleteView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["delete"]

    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response(status=status.HTTP_202_ACCEPTED)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class OrderContinueView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    
    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            request.session['order_id'] = order.pk
            return redirect('payment:payment_process_sandbox')
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)