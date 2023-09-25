from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Cart as CartModel, CartItem
from products.models import Product


class Cart:

    def __init__(self, request):
        """
        Initialize the cart
        """
        if request.user.is_authenticated is True:
            self.request = request
            self.user = request.user
            # cart = CartModel.objects.get(user=request.user)
            # if not cart:
            #     cart = CartModel.objects.create(user=request.user)
            cart, created = CartModel.objects.get_or_create(user=request.user)
            self.cart = cart
            # -----
            cart_session = request.session.get('cart')
            print(cart_session)
            if cart_session:

                for product_id, quantity in cart_session.items():

                    product = Product.objects.get(id=int(product_id))
                    cart_item, created = CartItem.objects.get_or_create(cart=self.cart, product=product, )

                    if created:
                        cart_item.quantity = int(quantity['quantity'])
                    else:
                        cart_item.quantity += int(quantity['quantity'])
                    cart_item.save()
                # Clear session cart
                del request.session['cart']
    # ________________________________________________________

    def add(self, product, quantity=1, Bool_to_replace=False):
        """
        Add the specified product to the cart if it exists
        """
        if self.request is not None and self.request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(cart=self.cart, product=product,)
            if created:
                cart_item.quantity = quantity
            elif Bool_to_replace:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()
            messages.success(self.request, _('Product successfully added to cart'))

# _______________________________________________________________________________________

    def remove(self, product):
        """
        Remove a product from the cart
        """
        if self.request.user.is_authenticated is True:
            cart_item = CartItem.objects.filter(cart=self.cart, product=product).first()
            if cart_item:
                cart_item.delete()
                messages.success(self.request, _('Product successfully removed from cart'))

    def save(self):
        """
        Mark session as modified to save changes
        """
        if self.request.user.is_authenticated is True:
            self.cart.save()

    def __iter__(self):
        if self.request.user.is_authenticated is True:
            for item in self.cart.items.all():
                item.total_price = item.get_total_price()
                yield item

    def __len__(self):
        if self.request.user.is_authenticated is True:
            return sum(item.quantity for item in self.cart.items.all())

    def clear(self):
        if self.request.user.is_authenticated is True:
            self.cart.items.all().delete()

    def get_total_price(self):
        if self.request.user.is_authenticated is True:
            return self.cart.get_total_price()

    def is_empty(self):
        if self.request.user.is_authenticated is True:
            return self.cart.items.count() == 0











