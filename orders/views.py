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
        try:
            cart = Cart.objects.get(user=request.user.id)
            cart_item = CartItem.objects.filter(cart=cart)
            data["items"] = [] 
            print(data, "eAFDSGthry4wted++++++"*100)


            for item in cart_item:
                item_data = {
                    "product": item.product.id,
                    "quantity": item.quantity,
                    "price": item.get_total_price()
                }
                print("@@@@@@@@@@@@@@@@@@@@"*10,"  > ", item_data)
                data["items"].append(item_data)



            order_form = OrderSerializer_e(data=data)
            print(order_form, "WWWWWWWWWW"*50)
            if order_form.is_valid():
                print("&"*200)
                order = order_form.validated_data
                print("$" * 200)
                order_obj = Order.objects.create(
        user=request.user,
        is_paid=False,
        first_name=order['first_name'],
        last_name=order['last_name'],
        phone_number=order['phone_number'],
        address=order['address'],
        order_notes=order['order_notes'],
    )
                print("#" * 200)
                for item in cart_item:
                    OrderItem.objects.create(
            order=order_obj,
            product=item.product,
            quantity=item.quantity,
            price=item.get_total_price(),
        )
                print("@" * 2000)
                return Response(status=status.HTTP_200_OK)
            else:
                print(order_form.errors, "^^"*50,order_form.error_messages,"^^"*50)
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