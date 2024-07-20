# payments/services.py
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import CircuitBreaker, CircuitBreakerError
from .strategies import PaymentStrategy

from .loggin_config import logger
from rest_framework.response import Response
# Initialize a circuit breaker instance
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_time=60)

class PaymentService:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
      

    def to_dict(self):
        return {
            'strategy': self.strategy.__class__.__name__,
            'message':'Payment Initiated Successfully'
        }
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def initiate_payment(self):
        try:
            # Call to payment strategy within the circuit breaker
            result = circuit_breaker.call(self.strategy.initiate_strategy_payment)
            if isinstance(result, CircuitBreakerError):
               logger.error(f"Function call resulted in an error: {result}")
               return Response({'error': str(result)}, status=500)
            else:
                return Response({'result': result})
        except Exception as e:
            logger.error(f"Payment initiation to the circuit breaker failed for order {self.order}: {e}")
            return e
