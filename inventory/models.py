from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=10)  # S, M, L, XL

    def __str__(self):
        return self.name

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(
        'Category',
        on_delete=models.PROTECT,
        related_name="products",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    sizes = models.ManyToManyField(Size, blank=True)
    
    def __str__(self):
        return self.product_name




class ProductVariant(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name="variants")
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)

    color = models.CharField(max_length=30, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])

    def __str__(self):

       return f"{self.product.product_name} - {self.size} - {self.color}"

class Store(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.location}"


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        DANGER = "DANGER", "Danger"
        SUCCESS = "SUCCESS", "Success"

    type = models.CharField(max_length=10, choices=NotificationType.choices)
    message = models.TextField()
    store = models.ForeignKey(
        "Store",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type}: {self.message}"


class Stock(models.Model):

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_items",
        null=True,
        blank=True
    )

    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="stock_items",
    )
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("variant", "store")

    def save(self, *args, **kwargs):
      old_quantity = None

      if self.pk:
        old_quantity = Stock.objects.get(pk=self.pk).quantity

      super().save(*args, **kwargs)

    # Only trigger if NEW or quantity changed
      if old_quantity != self.quantity:
        product_name = self.variant.product.product_name if self.variant else "Unknown"

        if self.quantity == 0:
            Notification.objects.create(
                type=Notification.NotificationType.DANGER,
                message=f"OUT OF STOCK: {product_name} at {self.store.name}",
                store=self.store,
            )
        elif self.quantity <= 5:
            Notification.objects.create(
                type=Notification.NotificationType.WARNING,
                message=f"LOW STOCK ALERT: {product_name} at {self.store.name}",
                store=self.store,
            )

    def __str__(self):
        return f"{self.variant.product.product_name} @ {self.store.name}: {self.quantity}"


class StockIn(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_ins",
        null= True,
        blank=True
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="stock_ins",
    )
    quantity_added = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # If this is an update, reverse the previous stock-in effect first.
        if self.pk:
            previous = StockIn.objects.get(pk=self.pk)
            previous_stock, _ = Stock.objects.get_or_create(
                variant=previous.variant,
                store=previous.store,
                defaults={"quantity": 0},
            )
            previous_stock.quantity -= previous.quantity_added
            previous_stock.save()

        super().save(*args, **kwargs)

        stock, _ = Stock.objects.get_or_create(
            variant=self.variant,
            store=self.store,
            defaults={"quantity": 0},
        )
        stock.quantity += self.quantity_added
        stock.save()

        product_name = self.variant.product.product_name if self.variant else "Unknown"
        Notification.objects.create(
            type=Notification.NotificationType.SUCCESS,
            message=(
                f"Stock added successfully: {product_name} +{self.quantity_added}"
            ),
            store=self.store,
        )

    def __str__(self):
        return f"IN {self.variant.product.product_name} +{self.quantity_added} ({self.store.name})"


class StockOut(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_outs",
        null= True,
        blank=True
    )
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="stock_outs",
    )
    quantity_sold = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # If this is an update, reverse the previous stock-out effect first.
        if self.pk:
            previous = StockOut.objects.get(pk=self.pk)
            previous_stock, _ = Stock.objects.get_or_create(
                variant=previous.variant,
                store=previous.store,
                defaults={"quantity": 0},
            )
            previous_stock.quantity += previous.quantity_sold
            previous_stock.save()

        super().save(*args, **kwargs)

        stock, _ = Stock.objects.get_or_create(
            variant=self.variant,
            store=self.store,
            defaults={"quantity": 0},
        )
        stock.quantity -= self.quantity_sold
        stock.save()

        product_name = self.variant.product.product_name if self.variant else "Unknown"

        Notification.objects.create(
            type=Notification.NotificationType.INFO,
            message=(
                f"Stock sold recorded: {product_name} -{self.quantity_sold}"
            ),
            store=self.store,
        )

    def __str__(self):
        return f"OUT {self.variant.product.product_name} -{self.quantity_sold} ({self.store.name})"


class Expense(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        BANK = "BANK", "Bank"
        MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"

    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=120, blank=True)
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CASH,
    )
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        total_expense = (
            Expense.objects.filter(store=self.store)
            .aggregate(total=Sum("amount"))
            .get("total")
            or 0
        )
        if total_expense > 10000:
            Notification.objects.create(
                type=Notification.NotificationType.WARNING,
                message=f"HIGH EXPENSE WARNING: {self.store.name}",
                store=self.store,
            )

    def __str__(self):
        return f"{self.title} ({self.store.name}) - {self.amount}"


class StockTransfer(models.Model):
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="transfers",
        null= True,
        blank=True
    )
    from_store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="stock_transfers_out",
    )
    to_store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name="stock_transfers_in",
    )
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # On update, undo the previous transfer before applying new values.
        if self.pk:
            previous = StockTransfer.objects.get(pk=self.pk)

            previous_from_stock, _ = Stock.objects.get_or_create(
                product=previous.product,
                store=previous.from_store,
                defaults={"quantity": 0},
            )
            previous_from_stock.quantity += previous.quantity
            previous_from_stock.save()

            previous_to_stock, _ = Stock.objects.get_or_create(
                product=previous.product,
                store=previous.to_store,
                defaults={"quantity": 0},
            )
            previous_to_stock.quantity -= previous.quantity
            previous_to_stock.save()

        super().save(*args, **kwargs)

        from_stock, _ = Stock.objects.get_or_create(
            Variant=self.variant,
            store=self.from_store,
            defaults={"quantity": 0},
        )
        from_stock.quantity -= self.quantity
        from_stock.save()

        to_stock, _ = Stock.objects.get_or_create(
            variant=self.variant,
            store=self.to_store,
            defaults={"quantity": 0},
        )
        to_stock.quantity += self.quantity
        to_stock.save()

        Notification.objects.create(
            type=Notification.NotificationType.INFO,
            message=(
                "Stock transferred successfully: "
                f"{self.product} x{self.quantity} "
                f"({self.from_store.name} -> {self.to_store.name})"
            ),
            store=self.to_store,
        )

    def __str__(self):
        return (
            f"Transfer {self.product} x{self.quantity}: "
            f"{self.from_store.name} -> {self.to_store.name}"
        )


class Sale(models.Model):
    store=models.ForeignKey(Store, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale #{self.id} - {self.created_at}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return self.quantity * self.price          
    
    def __str__(self):
       return f"{self.variant} x {self.quantity}"