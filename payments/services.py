# payments/services.py
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import CircuitBreaker
from .strategies import PaymentStrategy

logger = logging.getLogger(__name__)

# Initialize a circuit breaker instance
circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_time=60)

class PaymentService:
    def __init__(self, strategy: PaymentStrategy,order, user,total_amount):
        self.total_amount = total_amount
        self.strategy = strategy
        self.user= user
        self.order = order


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def initiate_payment(self):
        try:
            # Call to payment strategy within the circuit breaker
            return circuit_breaker.call(self.strategy.initiate_payment,self.total_amount,self.user,self.order)
        except Exception as e:
            logger.error(f"Payment initiation failed for order {self.order}: {e}")
            raise
