from decimal import Decimal
from django.test import TestCase
from box_selection.models import Product, Box, Order, OrderItem
from box_selection.services.box_selector import (
    get_item_orientations,
    items_overlap,
    can_place_item,
    can_pack_items,
    select_best_box,
)


class BoxSelectorServiceTests(TestCase):
    def setUp(self):
        # Sample standard boxes
        self.small_box = Box.objects.create(
            name="Small Box",
            internal_length=Decimal("20.00"),
            internal_width=Decimal("15.00"),
            internal_height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("10.00")
        )
        self.medium_box = Box.objects.create(
            name="Medium Box",
            internal_length=Decimal("40.00"),
            internal_width=Decimal("30.00"),
            internal_height=Decimal("20.00"),
            max_weight=Decimal("15.00"),
            cost=Decimal("25.00")
        )
        self.large_box = Box.objects.create(
            name="Large Box",
            internal_length=Decimal("60.00"),
            internal_width=Decimal("50.00"),
            internal_height=Decimal("40.00"),
            max_weight=Decimal("30.00"),
            cost=Decimal("50.00")
        )

    def test_1_one_product_fits_in_smallest_box(self):
        # Product easily fits in Small Box
        product = Product.objects.create(
            name="Phone", length=Decimal("15.00"), width=Decimal("8.00"), height=Decimal("2.00"), weight=Decimal("0.50")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        self.assertEqual(best_box.id, self.small_box.id)

    def test_2_product_does_not_fit_smallest_but_fits_larger_box(self):
        # Product dimension 30x20x5 exceeds small box (20x15x10) but fits in medium (40x30x20)
        product = Product.objects.create(
            name="Large Tablet", length=Decimal("30.00"), width=Decimal("20.00"), height=Decimal("5.00"), weight=Decimal("1.50")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        self.assertEqual(best_box.id, self.medium_box.id)

    def test_3_product_fits_after_rotation(self):
        # Box: 20x15x10
        # Product original dims: 8x18x12 (length 8, width 18, height 12 - width 18 > 15, height 12 > 10)
        # Rotated to: 18x12x8 (length 18 <= 20, width 12 <= 15, height 8 <= 10) -> fits!
        product = Product.objects.create(
            name="Book", length=Decimal("8.00"), width=Decimal("18.00"), height=Decimal("12.00"), weight=Decimal("1.00")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        self.assertEqual(best_box.id, self.small_box.id)

    def test_4_product_too_heavy_for_small_box(self):
        # Product dimensions fit small box (10x10x5), but weight is 6.00kg > small_box.max_weight (5.00kg)
        product = Product.objects.create(
            name="Lead Weight", length=Decimal("10.00"), width=Decimal("10.00"), height=Decimal("5.00"), weight=Decimal("6.00")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        # Must select medium_box because small_box cannot hold the weight
        self.assertEqual(best_box.id, self.medium_box.id)

    def test_5_multiple_products_fit_in_one_box(self):
        # Two products that both fit side-by-side in small box (20x15x10)
        p1 = Product.objects.create(name="P1", length=Decimal("10.00"), width=Decimal("15.00"), height=Decimal("5.00"), weight=Decimal("1.00"))
        p2 = Product.objects.create(name="P2", length=Decimal("10.00"), width=Decimal("15.00"), height=Decimal("5.00"), weight=Decimal("1.00"))
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=p1, quantity=1)
        OrderItem.objects.create(order=order, product=p2, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        self.assertEqual(best_box.id, self.small_box.id)

    def test_6_multiple_quantities(self):
        # 1 Product with quantity 3 (each 10x5x5) -> fits in small box 20x15x10
        product = Product.objects.create(name="Small Box Product", length=Decimal("10.00"), width=Decimal("5.00"), height=Decimal("5.00"), weight=Decimal("0.50"))
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=3)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        self.assertEqual(best_box.id, self.small_box.id)

    def test_7_items_touching_each_other_are_allowed(self):
        # Item 1 at (0,0,0) dim (10, 10, 10), Item 2 placed at (10, 0, 0) dim (10, 10, 10)
        pos1 = (0.0, 0.0, 0.0)
        dim1 = (10.0, 10.0, 10.0)
        pos2 = (10.0, 0.0, 0.0)
        dim2 = (10.0, 10.0, 10.0)

        # items_overlap should return False since they only touch at x=10
        self.assertFalse(items_overlap(pos1, dim1, pos2, dim2))

    def test_8_overlapping_items_are_rejected(self):
        # Overlap across all 3 axes
        pos1 = (0.0, 0.0, 0.0)
        dim1 = (10.0, 10.0, 10.0)
        pos2 = (5.0, 5.0, 5.0)
        dim2 = (10.0, 10.0, 10.0)

        self.assertTrue(items_overlap(pos1, dim1, pos2, dim2))

    def test_9_item_touching_box_boundary_is_allowed(self):
        # Box: 20x15x10, Item placed at (0,0,0) with exact dim (20, 15, 10)
        box_dims = (20.0, 15.0, 10.0)
        pos = (0.0, 0.0, 0.0)
        dim = (20.0, 15.0, 10.0)

        self.assertTrue(can_place_item(pos, dim, box_dims, []))

    def test_10_no_box_can_contain_the_product(self):
        # Product dimension 100x100x100 exceeds all available boxes (largest is 60x50x40)
        product = Product.objects.create(
            name="Gigantic Desk", length=Decimal("100.00"), width=Decimal("100.00"), height=Decimal("100.00"), weight=Decimal("5.00")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNone(best_box)

    def test_11_total_weight_exceeds_all_boxes(self):
        # Small dimensions (10x10x10) but weight is 50kg (max box capacity is 30kg)
        product = Product.objects.create(
            name="Dense Gold Bar", length=Decimal("10.00"), width=Decimal("10.00"), height=Decimal("10.00"), weight=Decimal("50.00")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNone(best_box)

    def test_12_exact_dimension_boundary(self):
        # Item dimensions exactly match small box internal dimensions: 20x15x10
        product = Product.objects.create(
            name="Exact Fit Item", length=Decimal("20.00"), width=Decimal("15.00"), height=Decimal("10.00"), weight=Decimal("1.00")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        self.assertEqual(best_box.id, self.small_box.id)

    def test_13_exact_maximum_weight_boundary(self):
        # Item weight exactly matches small box max weight: 5.00kg
        product = Product.objects.create(
            name="Exact Weight Item", length=Decimal("10.00"), width=Decimal("10.00"), height=Decimal("5.00"), weight=Decimal("5.00")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        self.assertEqual(best_box.id, self.small_box.id)

    def test_14_correct_box_chosen_when_multiple_boxes_work(self):
        # Product fits in Small Box (vol: 3000, cost: 10), Medium Box (vol: 24000, cost: 25), Large Box (vol: 120000, cost: 50)
        # System must select Small Box (smallest volume & lowest cost)
        product = Product.objects.create(
            name="Small Gadget", length=Decimal("5.00"), width=Decimal("5.00"), height=Decimal("5.00"), weight=Decimal("0.20")
        )
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        best_box = select_best_box(order)
        self.assertIsNotNone(best_box)
        self.assertEqual(best_box.id, self.small_box.id)
