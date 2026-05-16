from django.urls import path
from .views import add_product
from .views import product_list
from . import views
from .views import(
    sell_product, add_variant, product_list, add_stock_in, add_expense, expense_list,
)

urlpatterns = [
    path('add-product/', add_product, name='add_product'),
    path('products/',product_list, name='product_list'),
    path('add-variant/',add_variant, name='add_variant'),
    path('add-stock/', add_stock_in, name='add_stock_in'),
    path('add-expense/', add_expense, name='add_expense'),
    path('expenses/', expense_list, name='expense_list'),
    path('sell/<int:variant_id>/',views.sell_product, name='sell_product'),
    path('edit-variant/<int:variant_id>/', views.edit_variant, name='edit_variant'),
    path('delete-variant/<int:variant_id>/', views.delete_variant, name='delete_variant'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('edit-expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('stores/', views.store_list, name='store_list'),
    path('add-store/', views.add_store, name='add_store'),
    path('edit-store/<int:store_id>/', views.edit_store, name='edit_store'),
    path('delete-store/<int:store_id>/', views.delete_store, name='delete_store'),
    path('sales/', views.sales_list, name='sales_list'),
    path('categories/', views.category_list, name='category_list'),
    path('add-category/', views.add_category, name='add_category'),
    path('sizes/', views.size_list, name='size_list'),
    path('add-size/', views.add_size, name='add_size'),
    path('edit-category/<int:category_id>/',views.edit_category,name='edit_category'),
    path('delete-category/<int:category_id>/',views.delete_category,name='delete_category'),
    path('edit-size/<int:size_id>/',views.edit_size,name='edit_size'),
    path('delete-size/<int:size_id>/',views.delete_size,name='delete_size'),
    path('sell/<int:variant_id>/',views.sell_product,name='sell_product'),

]