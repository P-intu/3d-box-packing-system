from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, BoxViewSet, OrderViewSet, RecommendBoxView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'boxes', BoxViewSet, basename='box')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('orders/<int:order_id>/recommend-box/', RecommendBoxView.as_view(), name='order-recommend-box'),
    path('', include(router.urls)),
]
