from django.contrib import admin

from .models import (
    Category,
    Expense,
    Product,
    Stock,
    StockIn,
    StockOut,
    StockTransfer,
    Store,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_name", "category", "price")
    search_fields = ("product_name", "category__name")
    list_filter = ("category",)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "location")
    search_fields = ("name", "location")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("id", "store", "quantity")
    search_fields = ("store__name",)
    list_filter = ("store",)


@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display = ("id", "store", "quantity_added", "date")
    search_fields = ("store__name",)
    list_filter = ("store", "date")
    date_hierarchy = "date"


@admin.register(StockOut)
class StockOutAdmin(admin.ModelAdmin):
    list_display = ("id", "store", "quantity_sold", "date")
    search_fields = ("store__name",)
    list_filter = ("store", "date")
    date_hierarchy = "date"




@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("title", "store", "category", "payment_method", "amount", "date")
    search_fields = ("title", "category", "store__name")
    list_filter = ("store", "payment_method", "category", "date")
    date_hierarchy = "date"


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ("id", "from_store", "to_store", "quantity", "date")
    search_fields = ("from_store__name", "to_store__name")
    list_filter = ("from_store", "to_store", "date")
    date_hierarchy = "date"