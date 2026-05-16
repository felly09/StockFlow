from django import forms
from .models import Product
from django import forms
from .models import StockIn
from .models import ProductVariant
from .models import Expense
from .models import Store
from .models import Category, Size

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'price','image','sizes']
        widgets = {
            'sizes': forms.CheckboxSelectMultiple()
        }

    def clean_price(self):

       price = self.cleaned_data['price']

       if price < 0:

          raise forms.ValidationError(
            "Price cannot be negative."
        )

       return price    


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = ['variant', 'store', 'quantity_added']        



class ProductVariantForm(forms.ModelForm):

    class Meta:

        model = ProductVariant

        fields = ['product','size','color','price']

        widgets = {

            'price': forms.NumberInput(
                attrs={
                    'min': '0',
                    'step': '0.01'
                }
            )

        }

    def clean_price(self):

        price = self.cleaned_data['price']

        if price < 0:

            raise forms.ValidationError(
                "Price cannot be negative."
            )

        return price


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['store','title','description','amount', 'payment_method']   
        widgets = { 'amount': forms.NumberInput(attrs={'min':'0'})}
    def clean_amount(self):

      amount = self.cleaned_data['amount']

      if amount < 0:

        raise forms.ValidationError(
            "Amount cannot be negative."
        )

      return amount         

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'location']        


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name']

class SizeForm(forms.ModelForm):

    class Meta:
        model = Size
        fields = ['name']        