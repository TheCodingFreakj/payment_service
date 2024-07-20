# payments/services.py
import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import CircuitBreaker, CircuitBreakerError
from .strategies import PaymentStrategy
from django.http import JsonResponse
from .loggin_config import logger
from .logsProducer import send_log
from rest_framework.response import Response
# Initialize a circuit breaker instance
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_time=60)

class PaymentService:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def to_dict(self):
        return {
            'strategy': self.strategy.__class__.__name__,
            'message': 'Payment Initiated Successfully'
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def initiate_payment(self,transaction_id,user,ip_address):
        try:
            if (self.strategy.__class__.__name__ == None):
                raise Exception("Issue is there")
            logger.debug(f"Initiating payment for order using strategy {self.strategy.__class__.__name__}")
            
            # Call to payment strategy within the circuit breaker
            result = circuit_breaker.call(self.strategy.initiate_strategy_payment)
            
            logger.debug(f"Payment strategy succeeded------> {result}")
            return result
        
        except Exception as e:
            logger.error(f"Payment initiation to the circuit breaker failed: {e}")
            transaction_data = {
                    'transaction_id':transaction_id,
                    'user_id': user,
                    'payment_method': "POST",
                    'status': 'failed',
                    'failed_reason':str(e),
                    'initiated_at': datetime.datetime.now().isoformat(),
                    'location': ip_address
                }
                # Log the transaction initiation
            send_log({'type': 'transaction', 'data': transaction_data})
            error_data = {
            'error': str(e),
            'status': 'error'
            }
            return JsonResponse(error_data, status=500)
