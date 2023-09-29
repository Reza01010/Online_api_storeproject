from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework import generics, permissions
from products.serializers import CartSerializer, CartItemSerializer
from .cart import Cart
from .models import Cart as Cart_,CartItem
from products.models import Product
from .forms import AddToCartProductForm
from rest_framework import status


def geet_Product_object(pk):
    try:
        return Product.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def cart_detail_view(request):
    if request.method == 'GET':
        cart = CartSerializer(Cart(request))
        return Response({'cart': cart}, status=HTTP_200_OK)

    elif request.method == 'POST':
        serializes = CartSerializer(data=request.data)
        if serializes.is_valid():
            cleaned_data = serializes.validated_data
            quantity = cleaned_data['quantity']
            product = geet_Product_object(pk=int(cleaned_data['product']))
            cart = Cart(request)
            cart.add(product, quantity, Bool_to_replace=True)
            cart = CartSerializer(Cart(request))
            return Response({'cart': cart}, status=HTTP_200_OK)
        else:
            return Response(serializes.errors, status=HTTP_400_BAD_REQUEST)
    return Response(status=HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @authentication_classes([BasicAuthentication])
# @permission_classes([IsAuthenticated])
# def add_to_cart_view(request):
#     if request.method == 'POST':
#
#         serializes = CartItemSerializer(data=request.data)
#
#         if serializes.is_valid():
#
#             cleaned_data = serializes.validated_data
#             quantity = cleaned_data['quantity']
#             print(".."*100, quantity, " ------ ", cleaned_data['product'].id, ".."*100)
#             product = geet_Product_object(pk=int(cleaned_data['product'].id))
#             cart = Cart(request)
#             print(cart,".*."*100)
#             cart.add(product, quantity, Bool_to_replace=False)
#             print(Cart_.objects.get(user=request.user.id),".+=++++++++++."*100)
#             cart = CartSerializer(Cart(request))
#             return Response({'cart': cart}, status=HTTP_200_OK)
#         else:
#             return Response(serializes.errors, status=HTTP_400_BAD_REQUEST)


class AddToCartView(generics.CreateAPIView):
    queryset = Cart_.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post']

    def perform_create(self, serializer):
        user = self.request.user

        try:
            cart = Cart_.objects.get(user=user)

            cart_items = serializer.validated_data.get('items', [])
            for item in cart_items:
                product = item['product']
                quantity = item['quantity']
                try:
                    cart_item = CartItem.objects.get(cart=cart, product=product)
                    cart_item.quantity += quantity
                    cart_item.save()
                except CartItem.DoesNotExist:
                    CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        except Cart_.DoesNotExist:
            serializer.save(user=user)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    cart = Cart(request)

    product = geet_Product_object(pk=product_id)
    cart.remove(product)
    return Response(status=HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    cart = Cart(request)

    if len(cart):
        cart.clear()
        return Response({'message': 'All products successfully removed from your cart'}, status=HTTP_200_OK)
    else:
        return Response({'message': 'Your cart is already empty'}, status=HTTP_400_BAD_REQUEST)


