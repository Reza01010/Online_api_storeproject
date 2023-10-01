from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from django.urls import reverse
import requests
import json
from rest_framework import status
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import requests
import json
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from cart.tasks import send_order_confirmation_email
from orders.models import Order


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def payment_process_sandbox(request):
    # get order id from session
    print("1"*50)
    order_id = request.session.get('order_id')
    # ger the order object
    print("2"*50)
    order = get_object_or_404(Order, id=order_id)
    print("3"*50)
    toman_total_price = order.get_total_price()
    print("4"*50)
    rial_total_price = toman_total_price * 10
    print("5"*50)
    zarinpal_request_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'
    print("6"*50)
    request_header = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    print("7"*50)
    request_data = {
        'MerchantID': 'dddddddddddddddddddddddddddddddddddd',
        'Amount': rial_total_price,
        'Description': f"#{order.id} : {order.user.first_name}  {order.user.first_name}",
        # 'CallbackURL': '127.0.0.1:8000' + reverse("payment:payment_callback_sandbox"),
        'CallbackURL': request.build_absolute_uri(reverse("payment:payment_callback_sandbox")),
        # 'CallbackURL': f'127.0.0.1:8000{reverse("payment:payment_callback_sandbox")}',
    }
    print("8"*50)
    res = requests.post(url=zarinpal_request_url, data=json.dumps(request_data), headers=request_header)
    # print('>>>  ',res.json()['data'])###برای مثال ممکنه در حالت واقعی متفاوت باشه#
    # >>>   {'code':100, 'message':'Success', 'zarinpal_authority':'A00000000000000000000000000350631138', 'fee_type':'Merchant', 'fee':'15000'}
    print("9"*50)
    data = res.json()
    print("10"*50)
    authority = data['Authority']
    print("11"*50)
    order.zarinpal_authority = authority
    print("12"*50)
    order.save()
    print("13"*500)
    if 'errors' not in data or len(data['errors']) == 0:
        print('https://sandbox.zarinpal.com/pg/StartPay/{authority}'.format(authority=authority))
        return redirect('https://sandbox.zarinpal.com/pg/StartPay/{authority}'.format(authority=authority))
    else:
        return Response({'message': 'Error from zarinpal'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def payment_callback_sandbox(request):
    payment_authority = request.GET.get("Authority")
    payment_status = request.GET.get("Status")

    order = get_object_or_404(Order, zarinpal_authority=payment_authority)

    toman_total_price = order.get_total_price()
    rial_total_price = toman_total_price * 10

    if payment_status == 'OK':

        request_header = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        request_data = {
            'MerchantID': 'dddddddddddddddddddddddddddddddddddd',
            'Amount': rial_total_price,
            'Authority': payment_authority,

        }
        res = requests.post(url='https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json',
                            data=json.dumps(request_data),
                            headers=request_header, )

        if 'errors' not in res.json():
            data = res.json()
            payment_code = data['Status']

            if payment_code == 100:
                order.is_paid = True
                order.zarinpal_ref_id = data['RefID']
                order.zarinpal_data = data
                order.save()

                send_order_confirmation_email.delay(email=request.user.email, text='پرداخت با موفقیت انجام شد.')
                return Response({'message': 'پرداخت با موفقیت انجام شد.'}, status=status.HTTP_200_OK)

            elif payment_code == 101:
                return Response({'message': 'پرداخت با موفقیت انجام شد. البته این تراکنش قبلا ثبت شده!'}, status=status.HTTP_201_CREATED)

            else:
                error_code = res.json()['errors']['code']
                error_message = res.json()['errors']['message']
                send_order_confirmation_email.delay(email=request.user.email,
                                                    text=f'تراکنش ناموفق بود.  {error_code}     {error_message}')
                return Response({'message': f'تراکنش ناموفق بود.  {error_code}     {error_message}'}, status=status.HTTP_404_NOT_FOUND)
    else:

        return Response({'message': 'تراکنش ناموفق بود.'}, status=status.HTTP_404_NOT_FOUND)



