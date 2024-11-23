from django.urls import path
from .views import OrderAPIView, DetailOrderAPIView, PaymentGatewayAPIView

urlpatterns = [
    path('', OrderAPIView.as_view(), name='orders'),
    path('<int:pk>/', DetailOrderAPIView.as_view(), name='detail_order'),
    path('payment/<int:pk>/', PaymentGatewayAPIView.as_view(), name='payment'),
]
