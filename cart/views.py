from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from django.shortcuts import get_object_or_404

from .cart import Cart
from products.models import Product
from .forms import AddToCartProductForm


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_detail_view(request):
    cart = Cart(request)
    for item in cart:
        item['product_update_quantity_form'] = AddToCartProductForm(initial={
            'quantity': item['quantity'], 'inplace': True
        })
    return Response({'cart': cart}, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart_view(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)
    form = AddToCartProductForm(request.data)

    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data['quantity']
        cart.add(product, quantity, replase_current_quantity=cleaned_data['inplace'])
        return Response(status=HTTP_200_OK)
    else:
        return Response(form.errors, status=HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return Response(status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    cart = Cart(request)

    if len(cart):
        cart.clear()
        return Response({'message': 'All products successfully removed from your cart'}, status=HTTP_200_OK)
    else:
        return Response({'message': 'Your cart is already empty'}, status=HTTP_400_BAD_REQUEST)


