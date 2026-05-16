from django.db.models import Count, Sum

from inventory.models import Product, StockIn, StockOut, StockTransfer, Store
from inventory.models import Stock ,Notification, SaleItem


def get_top_selling_product():

    top = (
        SaleItem.objects
        .values(
            "variant__product__id",
            "variant__product__product_name"
        )
        .annotate(total_sold=Sum("quantity"))
        .order_by("-total_sold")
        .first()
    )

    return top


def get_most_active_store():
    stock_in_counts = StockIn.objects.values("store").annotate(cnt=Count("id"))
    stock_out_counts = StockOut.objects.values("store").annotate(cnt=Count("id"))
    transfer_out_counts = (
        StockTransfer.objects.values("from_store")
        .annotate(cnt=Count("id"))
        .values("from_store", "cnt")
    )
    transfer_in_counts = (
        StockTransfer.objects.values("to_store")
        .annotate(cnt=Count("id"))
        .values("to_store", "cnt")
    )

    activity_map = {}

    for row in stock_in_counts:
        activity_map[row["store"]] = activity_map.get(row["store"], 0) + row["cnt"]
    for row in stock_out_counts:
        activity_map[row["store"]] = activity_map.get(row["store"], 0) + row["cnt"]
    for row in transfer_out_counts:
        store_id = row["from_store"]
        activity_map[store_id] = activity_map.get(store_id, 0) + row["cnt"]
    for row in transfer_in_counts:
        store_id = row["to_store"]
        activity_map[store_id] = activity_map.get(store_id, 0) + row["cnt"]

    if not activity_map:
        return None

    most_active_store_id = max(activity_map, key=activity_map.get)
    return Store.objects.filter(pk=most_active_store_id).first()


def get_sales_summary():

    total_units_sold = (
        SaleItem.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )

    total_stock_in = (
        Stock.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )

    total_transferred = (
        StockTransfer.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )

    return {
        "total_units_sold": total_units_sold,
        "total_stock_in": total_stock_in,
        "total_transferred": total_transferred,
    }

def check_low_stock():
    low_items = Stock.objects.filter(quantity__lte=5)

    for item in low_items:
        product_name = item.variant.product.product_name if item.variant else "Unknown"

        Notification.objects.get_or_create(
            type=Notification.NotificationType.WARNING,
            message=f"Low stock: {product_name} - {item.variant} ({item.quantity})",
            store=item.store
        )