from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework import generics, permissions
from products.serializers import CartSerializer, CartItemSerializer, RemoveAllSerializer
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


@api_view(['GET', 'POST', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def cart_detail_view(request):
    if request.method == 'GET':
        cart = CartSerializer(Cart_.objects.get(user=request.user.id))

        return Response({'cart': cart.data}, status=HTTP_200_OK)

    elif request.method == 'POST':
        serializes = CartSerializer(data=request.data)
        if serializes.is_valid():
            cleaned_data = serializes.validated_data.get('items', [])
            quantity = cleaned_data[0]['quantity']
            product = geet_Product_object(pk=int(cleaned_data[0]['product'].id))

            cart, w_cart = Cart_.objects.get_or_create(user=request.user.id)

            if cart:
                try:
                    cart_item = CartItem.objects.get(cart=cart, product=product)
                    cart_item.quantity = quantity
                    cart_item.save()
                except CartItem.DoesNotExist:
                    cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
                    cart_item.save()

            elif w_cart:
                cart_item = CartItem.objects.create(cart=w_cart, product=product, quantity=quantity)
                cart_item.save()

            cart = CartSerializer(Cart_.objects.get(user=request.user.id))
            return Response({'cart': cart.data}, status=HTTP_200_OK)
        else:
            return Response(serializes.errors, status=HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        data = request.data
        serializer = RemoveAllSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            product_ids = serializer.validated_data.get('product_ids', [])
            remove_all = serializer.validated_data.get('remove_all', False)
            try:
                if remove_all == True:
                    cart = Cart_.objects.get(user=request.user.id)
                    cart_item = CartItem.objects.filter(cart=cart)
                    cart_item.delete()
                elif remove_all == False:
                    if isinstance(product_ids, list):
                        if all(isinstance(item, int) for item in product_ids):
                            cart = Cart_.objects.get(user=request.user.id)
                            item = CartItem.objects.filter(product__in=product_ids)
                            item.delete()
                        else:
                            return Response(status=HTTP_400_BAD_REQUEST)
                    else:

                        return Response(status=HTTP_400_BAD_REQUEST)
            except:
                return Response(status=HTTP_400_BAD_REQUEST)

            cart = CartSerializer(Cart_.objects.get(user=request.user.id))
            return Response({'cart': cart.data}, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    return Response(status=HTTP_400_BAD_REQUEST)


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



