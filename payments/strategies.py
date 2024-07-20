# payments/strategies.py
import datetime
import razorpay
import requests
import logging
from .logsProducer import send_log, get_user_location
from .models import Payment
from django.conf import settings
from .loggin_config import logger
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def initiate_strategy_payment(self):
        pass
class StripePaymentStrategy(PaymentStrategy):
    def initiate_strategy_payment(self, order):
        try:
            response = requests.post('https://stripe.example.com/pay', json={
                'order_id': order.id,
                'amount': order.total_amount,
                'user_id': order.user.id
            })
            response.raise_for_status()
            payment_data = response.json()

            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status=payment_data['status'],
                transaction_id=payment_data.get('transaction_id')
            )
            return payment
        except requests.RequestException as e:
            logger.error(f"Stripe payment initiation failed for order {order.id}: {e}")
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status='failure'
            )
            raise

class PayPalPaymentStrategy(PaymentStrategy):
    def initiate_strategy_payment(self, order):
        try:
            response = requests.post('https://paypal.example.com/pay', json={
                'order_id': order.id,
                'amount': order.total_amount,
                'user_id': order.user.id
            })
            response.raise_for_status()
            payment_data = response.json()

            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status=payment_data['status'],
                transaction_id=payment_data.get('transaction_id')
            )
            return payment
        except requests.RequestException as e:
            logger.error(f"PayPal payment initiation failed for order {order.id}: {e}")
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status='failure'
            )
            raise


class RazorPayStrategy(PaymentStrategy):
    def __init__(self,order_id, user,total_amount, transaction_id, ip_address):
        self.order_id = order_id
        self.user = user
        self.total_amount = total_amount
        self.ip_address = ip_address
        self.transaction_id = transaction_id
# settings.RAZORPAY_KEY_ID
    def initiate_strategy_payment(self):
        try:
            logger.debug(f"Initiating RazorPay payment for order {self.order_id}, user {self.user}, amount {self.total_amount}")

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            razorpay_order = client.order.create(
                {"amount": int(self.total_amount) * 100, "currency": "INR", "payment_capture": "1"}
            )

            logger.debug(f"RazorPay order created: {razorpay_order}")

            payment = Payment.objects.create(
                order=self.order_id,
                amount=self.total_amount,
                status=razorpay_order['status'],
                transaction_id=razorpay_order.get('id')
            )

            logger.debug(f"Payment object created in the database: {payment}")
            transaction_data = {
                    'transaction_id':self.transaction_id,
                    'user_id': self.user,
                    'payment_method': "POST",
                    'status': 'processing',
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': self.ip_address
                }
                # Log the transaction initiation
            send_log({'type': 'transaction', 'data': transaction_data})
            return {
                'order_id': self.order_id,
                'user': self.user,
                'total_amount': self.total_amount,
                'payment_method': 'razorpay'
            }
            
        except requests.RequestException as e:
            logger.error(f"RazorPay payment initiation failed for order {self.order_id}: {e}")
            Payment.objects.create(
                order=self.order_id,
                amount=self.total_amount,
                status='failure'
            )
            transaction_data = {
                    'transaction_id':self.transaction_id,
                    'user_id': self.user,
                    'payment_method': "POST",
                    'status': 'failed',
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': self.ip_address
                }
                # Log the transaction initiation
            send_log({'type': 'transaction', 'data': transaction_data})
            raise