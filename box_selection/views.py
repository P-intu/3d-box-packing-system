from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Product, Box, Order
from .serializers import ProductSerializer, BoxSerializer, OrderSerializer
from .services.box_selector import select_best_box


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Products.
    """
    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer


class BoxViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Boxes.
    """
    queryset = Box.objects.all().order_by('id')
    serializer_class = BoxSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Orders and their nested items.
    """
    queryset = Order.objects.prefetch_related('items__product').all().order_by('-created_at')
    serializer_class = OrderSerializer


class RecommendBoxView(APIView):
    """
    POST /api/orders/<order_id>/recommend-box/
    Dedicated APIView to recommend the best single box for a given order.
    """
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        recommended_box = select_best_box(order)
        
        if recommended_box is None:
            return Response(
                {
                    "success": False,
                    "message": "No suitable single box found for this order.",
                    "recommended_box": None
                },
                status=status.HTTP_200_OK
            )

        box_data = BoxSerializer(recommended_box).data
        return Response(
            {
                "success": True,
                "message": "Suitable box found.",
                "recommended_box": box_data
            },
            status=status.HTTP_200_OK
        )
