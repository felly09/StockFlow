from django.shortcuts import render,redirect,get_object_or_404
from .forms import ProductForm
from .models import Product
from .utils import check_low_stock
from .utils import reduce_stock
from django.shortcuts import redirect
from inventory.models import Stock, ProductVariant
from .forms import StockInForm, ProductVariantForm
from .models import ProductVariant, Stock
from .models import Sale, SaleItem
from django.contrib import messages
from .models import Expense,Store, Size, Category
from .forms import ExpenseForm, StoreForm, CategoryForm, SizeForm
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)  
        if form.is_valid():
            form.save()
            return redirect('dashboard')  
    else:
        form = ProductForm()

    return render(request, "inventory/add_product.html", {"form": form})

@login_required
def product_list(request):
    
    check_low_stock()

    products = Product.objects.prefetch_related('variants').all()

    stock_map = {
        s.variant_id: s.quantity for s in Stock.objects.all()
    }

    context = {
        "products": products,
        "stock_map": stock_map
    }

    return render(request, "inventory/product_list.html", context)

@login_required
def add_variant(request):
    if request.method =="POST":   
       form = ProductVariantForm(request.POST or None)
       if form.is_valid():
         form.save()
         return redirect('product_list')

    else:
        form = ProductVariantForm() 

    return render(request, 'inventory/add_variant.html', {'form': form})

@login_required
def add_stock_in(request):
    form = StockInForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'inventory/add_stock.html', {'form': form})


@login_required
def add_expense(request):
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('expense_list')
    return render(request, 'inventory/add_expense.html', {'form': form})  

@login_required
def expense_list(request):
    expenses = Expense.objects.all()
    return render(request, 'inventory/expense_list.html', {'expenses': expenses})     

@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    form = ExpenseForm(request.POST or None, instance=expense)

    if form.is_valid():
        form.save()
        messages.success(request, "Expense updated successfully!")
        return redirect("expense_list")

    return render(request, "inventory/edit_expense.html", {
        "form": form
    })

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)

    expense.delete()

    messages.success(request, "Expense deleted successfully!")

    return redirect("expense_list")           

@login_required
def edit_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.method == "POST":
        form = ProductVariantForm(request.POST, instance=variant)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductVariantForm(instance=variant)

    return render(request, "inventory/edit_variant.html", {"form": form})    

@login_required
def delete_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.method == "POST":
        variant.delete()
        return redirect('product_list')

    return render(request, "inventory/delete_variant.html", {"variant": variant})    

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, "inventory/edit_product.html", {"form": form})   

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect('product_list')

    return render(request, "inventory/delete_product.html", {"product": product})     

@login_required
def sell_product(request, variant_id):

    variant = get_object_or_404(ProductVariant, id=variant_id)

    stock_obj = Stock.objects.filter(variant=variant).first()

    if request.method == "POST":

        quantity = int(request.POST.get("quantity"))

        # safety check
        if not stock_obj:
            messages.error(request, "No stock found!")
            return redirect('product_list')

        # prevent negative stock
        if quantity > stock_obj.quantity:
            messages.error(request, "Not enough stock available!")
            return redirect('sell_product', variant_id=variant.id)

        price = variant.price
        total = quantity * price

        # create sale FIRST (recommended)
        store = stock_obj.store
        sale = Sale.objects.create(store=store,total_amount=total)

        # create sale item
        SaleItem.objects.create(
            sale=sale,
            variant=variant,
            quantity=quantity,
            price=price
        )

        # reduce stock
        stock_obj.quantity -= quantity
        stock_obj.save()

        messages.success(request, "Sale completed successfully!")
        return redirect('product_list')

    return render(request, "inventory/sell_product.html", {
        "variant": variant,
        "stock": stock_obj
    })

@login_required    
def sales_list(request):

    sales = SaleItem.objects.select_related(
        'sale',
        'variant',
        'sale__store'
    ).all().order_by('-sale__created_at')

    return render(request, 'inventory/sales_list.html', {
        'sales': sales
    })       

@login_required
def add_store(request):
    form = StoreForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('expense_list')

    return render(request, 'inventory/add_store.html', {
        'form': form
    })

@login_required
def store_list(request):
    stores = Store.objects.all()

    return render(request, 'inventory/store_list.html', {
        'stores': stores
    })

@login_required
def edit_store(request, store_id):
    store = get_object_or_404(Store, id=store_id)

    form = StoreForm(request.POST or None, instance=store)

    if form.is_valid():
        form.save()
        return redirect('store_list')

    return render(request, 'inventory/edit_store.html', {'form': form})


@login_required
def delete_store(request, store_id):

    store = get_object_or_404(Store, id=store_id)

    try:

        store.delete()

        messages.success(
            request,
            "Store deleted successfully."
        )

    except ProtectedError:

        messages.error(
            request,
            "Cannot delete store because records are using it."
        )

    return redirect('store_list')

@login_required
def add_category(request):

    form = CategoryForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('category_list')

    return render(request, 'inventory/add_category.html', {
        'form': form
    })

@login_required
def category_list(request):

    categories = Category.objects.all()

    return render(request, 'inventory/category_list.html', {
        'categories': categories
    })    

@login_required
def add_size(request):

    form = SizeForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('size_list')

    return render(request, 'inventory/add_size.html', {
        'form': form
    })

@login_required
def size_list(request):

    sizes = Size.objects.all()

    return render(request, 'inventory/size_list.html', {
        'sizes': sizes
    }) 


@login_required
def edit_size(request, size_id):

    size = get_object_or_404(Size, id=size_id)

    form = SizeForm(
        request.POST or None,
        instance=size
    )

    if form.is_valid():
        form.save()
        return redirect('size_list')

    return render(request, 'inventory/edit_size.html', {
        'form': form
    })

@login_required
def delete_size(request, size_id):
    size = get_object_or_404(Size, id=size_id)

    try:

        size.delete()

        messages.success(
            request,
            "Size deleted successfully."
        )

    except ProtectedError:

        messages.error(
            request,
            "Cannot delete size because variants are using it."
        )

    return redirect('size_list')
               
@login_required 
def edit_category(request, category_id):

    category = get_object_or_404(Category, id=category_id)

    form = CategoryForm(
        request.POST or None,
        instance=category
    )

    if form.is_valid():
        form.save()
        return redirect('category_list')

    return render(request, 'inventory/edit_category.html', {
        'form': form
    })

@login_required
def delete_category(request, category_id):

    category = get_object_or_404(Category, id=category_id)

    try:
        category.delete()

        messages.success(
            request,
            "Category deleted successfully."
        )

    except ProtectedError:

        messages.error(
            request,
            "Cannot delete category because products are using it."
        )

    return redirect('category_list')     