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
        
        logger.debug(f"Received payment request: order_id={order_id}, total_amount={total_amount}, payment_method={payment_method}")

        try:
            if payment_method == 'stripe':
                payment_strategy = StripePaymentStrategy(order_id, user, total_amount)
                logger.debug(f"Selected StripePaymentStrategy for order_id={order_id}")
            elif payment_method == 'paypal':
                payment_strategy = PayPalPaymentStrategy(order_id, user, total_amount)
                logger.debug(f"Selected PayPalPaymentStrategy for order_id={order_id}")
            elif payment_method == 'razorpay':
                payment_strategy = RazorPayStrategy(order_id, user, total_amount)
                logger.debug(f"Selected RazorPayStrategy for order_id={order_id}")
            else:
                logger.error(f"Invalid payment method: {payment_method}")
                return Response({'status': 'error', 'message': 'Invalid payment method.'}, status=status.HTTP_400_BAD_REQUEST)
            
            payment_service = PaymentService(payment_strategy)
            logger.debug(f"Created PaymentService for order_id={payment_service.initiate_payment}")
            response = payment_service.initiate_payment()
            logger.debug(f"Logging the response={response}")
            return Response({'status': 'success', 'message': response}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Payment initiation failed for order {order_id}: {e}")
            return Response({'status': 'error', 'message': 'Payment initiation failed. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
