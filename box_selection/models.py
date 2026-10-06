from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Product(models.Model):
    """
    Represents an individual product item that can be ordered and packed into boxes.
    Dimensions are in appropriate numeric units (e.g., cm) and weight in kg/g.
    """
    name = models.CharField(max_length=255)
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Length of the product (must be > 0)"
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Width of the product (must be > 0)"
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Height of the product (must be > 0)"
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Weight of the product (must be > 0)"
    )

    def __str__(self):
        return f"{self.name} ({self.length}x{self.width}x{self.height}, wt: {self.weight})"


class Box(models.Model):
    """
    Represents a candidate shipping box with internal dimensions, max weight capacity, and cost.
    """
    name = models.CharField(max_length=255)
    internal_length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal length of the box (must be > 0)"
    )
    internal_width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal width of the box (must be > 0)"
    )
    internal_height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal height of the box (must be > 0)"
    )
    max_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Maximum weight capacity of the box (must be > 0)"
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost of the box (must be >= 0)"
    )

    def __str__(self):
        return f"{self.name} ({self.internal_length}x{self.internal_width}x{self.internal_height}, max_wt: {self.max_weight}, cost: {self.cost})"


class Order(models.Model):
    """
    Represents a customer order containing one or more products.
    """
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else 'New'})"


class OrderItem(models.Model):
    """
    Represents an item within an order, linking to a specific Product and specifying quantity.
    """
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity of product (must be >= 1)"
    )

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order #{self.order.id})"
