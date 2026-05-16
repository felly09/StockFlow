from .models import Stock
from .models import Stock, Notification

def check_low_stock():

    low_items = Stock.objects.filter(quantity__lte=5)

    for item in low_items:

        if not item.variant:
            continue

        product_name = item.variant.product.product_name

        variant_details = f"{item.variant.size} - {item.variant.color}"

        exists = Notification.objects.filter(
            message__icontains=product_name,
            type="WARNING"
        ).exists()

        if not exists:

            Notification.objects.create(
                type="WARNING",

                message=f"Low stock: {product_name} ({variant_details}) - {item.quantity} left"
            )

def reduce_stock(product, size, qty):
    stock = ProductStock.objects.get(product=product, size=size)

    if stock.quantity >= qty:
        stock.quantity -= qty
        stock.save()
        return True
    return False        

def dashboard(request):
    check_low_stock()

    context = {
        "top_product": get_top_selling_product(),
        "active_store": get_most_active_store(),
        "summary": get_sales_summary(),
    }

    return render(request, "analytics/dashboard.html", context)    