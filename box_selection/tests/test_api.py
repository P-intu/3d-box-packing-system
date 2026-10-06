from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from box_selection.models import Product, Box, Order, OrderItem


class ProductAPITests(APITestCase):
    def test_create_product(self):
        url = reverse('product-list')
        data = {
            "name": "Tablet",
            "length": "25.00",
            "width": "18.00",
            "height": "1.00",
            "weight": "0.50"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, "Tablet")

    def test_list_products(self):
        Product.objects.create(name="P1", length=Decimal("10.0"), width=Decimal("10.0"), height=Decimal("10.0"), weight=Decimal("1.0"))
        Product.objects.create(name="P2", length=Decimal("20.0"), width=Decimal("20.0"), height=Decimal("20.0"), weight=Decimal("2.0"))
        url = reverse('product-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_product(self):
        p = Product.objects.create(name="P1", length=Decimal("10.0"), width=Decimal("10.0"), height=Decimal("10.0"), weight=Decimal("1.0"))
        url = reverse('product-detail', args=[p.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "P1")

    def test_create_product_invalid_data(self):
        url = reverse('product-list')
        data = {
            "name": "Bad Product",
            "length": "-10.00",
            "width": "18.00",
            "height": "1.00",
            "weight": "0.00"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('length', response.data)
        self.assertIn('weight', response.data)


class BoxAPITests(APITestCase):
    def test_create_box(self):
        url = reverse('box-list')
        data = {
            "name": "Medium Shipping Box",
            "internal_length": "40.00",
            "internal_width": "30.00",
            "internal_height": "20.00",
            "max_weight": "15.00",
            "cost": "25.50"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Box.objects.count(), 1)
        self.assertEqual(Box.objects.get().name, "Medium Shipping Box")

    def test_list_boxes(self):
        Box.objects.create(name="B1", internal_length=Decimal("20.0"), internal_width=Decimal("20.0"), internal_height=Decimal("20.0"), max_weight=Decimal("5.0"), cost=Decimal("10.0"))
        url = reverse('box-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_box(self):
        b = Box.objects.create(name="B1", internal_length=Decimal("20.0"), internal_width=Decimal("20.0"), internal_height=Decimal("20.0"), max_weight=Decimal("5.0"), cost=Decimal("10.0"))
        url = reverse('box-detail', args=[b.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "B1")

    def test_create_box_invalid_data(self):
        url = reverse('box-list')
        data = {
            "name": "Invalid Box",
            "internal_length": "40.00",
            "internal_width": "30.00",
            "internal_height": "20.00",
            "max_weight": "-5.00",
            "cost": "-10.00"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('max_weight', response.data)
        self.assertIn('cost', response.data)


class OrderAPITests(APITestCase):
    def setUp(self):
        self.p1 = Product.objects.create(name="Laptop", length=Decimal("35.00"), width=Decimal("25.00"), height=Decimal("2.00"), weight=Decimal("2.20"))
        self.p2 = Product.objects.create(name="Mouse", length=Decimal("12.00"), width=Decimal("7.00"), height=Decimal("4.00"), weight=Decimal("0.15"))

    def test_create_single_product_order(self):
        url = reverse('order-list')
        data = {
            "items": [
                {"product": self.p1.id, "quantity": 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(response.data['items'][0]['product'], self.p1.id)

    def test_create_multiple_product_order(self):
        url = reverse('order-list')
        data = {
            "items": [
                {"product": self.p1.id, "quantity": 1},
                {"product": self.p2.id, "quantity": 2}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get()
        self.assertEqual(order.items.count(), 2)

    def test_create_order_quantity_greater_than_one(self):
        url = reverse('order-list')
        data = {
            "items": [
                {"product": self.p2.id, "quantity": 5}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['items'][0]['quantity'], 5)

    def test_create_order_invalid_product(self):
        url = reverse('order-list')
        data = {
            "items": [
                {"product": 99999, "quantity": 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_quantity(self):
        url = reverse('order-list')
        data = {
            "items": [
                {"product": self.p1.id, "quantity": 0}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_order(self):
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=self.p1, quantity=2)
        url = reverse('order-detail', args=[order.id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['product_name'], "Laptop")


class RecommendationAPITests(APITestCase):
    def setUp(self):
        self.small_box = Box.objects.create(
            name="Small Box", internal_length=Decimal("20.00"), internal_width=Decimal("15.00"), internal_height=Decimal("10.00"), max_weight=Decimal("5.00"), cost=Decimal("10.00")
        )
        self.medium_box = Box.objects.create(
            name="Medium Box", internal_length=Decimal("40.00"), internal_width=Decimal("30.00"), internal_height=Decimal("20.00"), max_weight=Decimal("15.00"), cost=Decimal("25.00")
        )

    def test_successful_recommendation(self):
        phone = Product.objects.create(name="Phone", length=Decimal("15.00"), width=Decimal("8.00"), height=Decimal("2.00"), weight=Decimal("0.50"))
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=phone, quantity=1)

        url = reverse('order-recommend-box', args=[order.id])
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['recommended_box']['id'], self.small_box.id)

    def test_larger_box_selected(self):
        laptop = Product.objects.create(name="Laptop", length=Decimal("35.00"), width=Decimal("25.00"), height=Decimal("2.00"), weight=Decimal("2.20"))
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=laptop, quantity=1)

        url = reverse('order-recommend-box', args=[order.id])
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['recommended_box']['id'], self.medium_box.id)

    def test_rotation_recommendation(self):
        book = Product.objects.create(name="Book", length=Decimal("8.00"), width=Decimal("18.00"), height=Decimal("12.00"), weight=Decimal("1.00"))
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=book, quantity=1)

        url = reverse('order-recommend-box', args=[order.id])
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['recommended_box']['id'], self.small_box.id)

    def test_no_suitable_box(self):
        desk = Product.objects.create(name="Desk", length=Decimal("100.00"), width=Decimal("100.00"), height=Decimal("100.00"), weight=Decimal("5.00"))
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=desk, quantity=1)

        url = reverse('order-recommend-box', args=[order.id])
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['success'])
        self.assertIsNone(response.data['recommended_box'])

    def test_invalid_order_id_returns_404(self):
        url = reverse('order-recommend-box', args=[99999])
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
