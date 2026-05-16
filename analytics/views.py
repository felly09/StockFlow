from django.shortcuts import render
from .utils import get_most_active_store, get_sales_summary, get_top_selling_product
from inventory.models import Notification
from .utils import check_low_stock
from inventory.models import Stock


def dashboard(request):
    check_low_stock()

    context = {
        "top_product": get_top_selling_product(),
        "active_store": get_most_active_store(),
        "summary": get_sales_summary(),
        "notifications": Notification.objects.order_by('-created_at')[:10],  # 👈 ADD THIS
        "stock_items": Stock.objects.all(),
    }

    return render(request, "analytics/dashboard.html", context)