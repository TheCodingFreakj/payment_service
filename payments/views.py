# orders/viewsets.py
import logging
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import  PaymentService
from .strategies import StripePaymentStrategy, PayPalPaymentStrategy,RazorPayStrategy


logger = logging.getLogger(__name__)

class PaymentsViewSet(viewsets.ViewSet):
    def create(self, request):
        user = 1
        order_id = request.data.get('order_id')
        total_amount = request.data.get('total_amount')
        payment_method = request.data.get('payment_type')  # e.g., 'stripe' or 'paypal'
        
        try:
            if payment_method == 'stripe':
                payment_strategy = StripePaymentStrategy()
            elif payment_method == 'paypal':
                payment_strategy = PayPalPaymentStrategy()
            elif payment_method == 'razorpay':
                payment_strategy = RazorPayStrategy()    
            else:
                return Response({'status': 'error', 'message': 'Invalid payment method.'}, status=status.HTTP_400_BAD_REQUEST)
            payment_service = PaymentService(payment_strategy)
            return payment_service.initiate_payment(total_amount,user,order_id)
           
        except Exception as e:
            logger.error(f"Payment initiation failed for order {payment_service.id}: {e}")
            return Response({'status': 'error', 'message': 'Payment initiation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
