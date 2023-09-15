from pyexpat import model

from django import forms


class AddToCartProductForm(forms.Form):
    # QUANTITY_CHOICES = [
    #     (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'),
    #     (11, '11'), (12, '12'), (..., '...'), (30, '30'),
    # ]

    QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 31)]

    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)

    inplace = forms.BooleanField(required=False,widget=forms.HiddenInput)

class Myaccountfrom(forms.Form):
    firstname = forms.CharField(required=False)
    username = forms.CharField(required=False)
    lastname = forms.CharField(required=False)
    email = forms.EmailField(required=False)