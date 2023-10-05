from rest_framework import serializers
from .models import Product, Comment, UserFavorite, Contact_us
from orders.models import Order,OrderItem
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist


from rest_framework import serializers
from cart.models import Cart, CartItem


class RemoveAllSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), required=False)
    remove_all = serializers.BooleanField(required=False)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', )


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('product', 'quantity', )


# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True)
#     total_price = serializers.SerializerMethodField()
#     user = UserSerializer(read_only=True)
#
#     class Meta:
#         model = Cart
#         fields = ('user', 'created_at', 'updated_at', 'items', 'total_price')
#
#     def create(self, validated_data):
#         items_data = validated_data.pop('items')
#         cart = Cart.objects.create(**validated_data)
#         for item_data in items_data:
#             CartItem.objects.create(cart=cart, **item_data)
#         return cart

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True,)
    total_price = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ('user', 'created_at', 'updated_at', 'items', 'total_price')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        cart = Cart.objects.create(**validated_data)
        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)
        return cart

    def get_total_price(self, obj):
        # Calculate the total price of the cart
        total_price = 0

        try:
            for item in obj.items.all():
                total_price += item.product.price * item.quantity
        except AttributeError:
            for item in obj['items']:
                total_price += item['product'].price * item['quantity']
        return total_price


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['author', 'active']


class ProductSerializer_d(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class UserFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFavorite
        fields = '__all__'


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_us
        exclude = ['user', ]


class MyAccountSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'username']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']


class OrderSerializer_e(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        exclude = ['user', 'is_paid', 'zarinpal_authority', 'zarinpal_ref_id', 'zarinpal_data']


class OrderSerializer_e_t(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ['user', 'is_paid', 'zarinpal_authority', 'zarinpal_ref_id', 'zarinpal_data']
