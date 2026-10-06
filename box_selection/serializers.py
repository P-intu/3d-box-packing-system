from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from .models import Product, Box, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'length', 'width', 'height', 'weight']

    def validate_length(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Length must be greater than 0.")
        return value

    def validate_width(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Width must be greater than 0.")
        return value

    def validate_height(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Height must be greater than 0.")
        return value

    def validate_weight(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Weight must be greater than 0.")
        return value


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['id', 'name', 'internal_length', 'internal_width', 'internal_height', 'max_weight', 'cost']

    def validate_internal_length(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Internal length must be greater than 0.")
        return value

    def validate_internal_width(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Internal width must be greater than 0.")
        return value

    def validate_internal_height(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Internal height must be greater than 0.")
        return value

    def validate_max_weight(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Max weight must be greater than 0.")
        return value

    def validate_cost(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError("Cost cannot be negative.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'items']
        read_only_fields = ['id', 'created_at']

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("An order must contain at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for item_data in items_data:
                OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if items_data is not None:
                instance.items.all().delete()
                for item_data in items_data:
                    OrderItem.objects.create(order=instance, **item_data)
        return instance
