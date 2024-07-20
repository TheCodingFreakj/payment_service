import datetime
import logging
import time
from .logsProducer import send_log, get_user_location
# Configure the logging
logging.basicConfig(level=logging.debug)
from .loggin_config import logger

class CircuitBreakerError(Exception):
    def __init__(self, original_exception, message="Circuit breaker triggered"):
        super().__init__(f"{message}: {original_exception}")
        self.original_exception = original_exception
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_time=60):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'
        logger.debug("Initialized CircuitBreaker with failure_threshold=%d, recovery_time=%d", failure_threshold, recovery_time)
        
    def call(self, func, *args, **kwargs):
        logger.debug("CircuitBreaker call: state=%s, failures=%d", self.state, self.failures)
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_time:
                self.state = 'HALF-OPEN'
                logger.debug("Transitioning to HALF-OPEN state")
            else:
                logger.warning("Circuit breaker is open. Cannot call function.")
                return CircuitBreakerError('Circuit breaker is open')

        try:
            result = func(*args, **kwargs)
            logger.debug(f"Function call successful for args: {args}")
            logger.debug(f"Function call successful for kwargs: {kwargs}")
            self.reset()
            logger.debug(f"Function call successful, result: {result}")
            transaction_data = {
                'transaction_id': "transaction_id",
                'user_id': 1,
                'payment_method': "POST",
                'status': 'processing',
                'initiated_at': datetime.datetime.now().isoformat(),
                'location': get_user_location("ip_address")
            }
            # Log the transaction initiation
            send_log({'type': 'transaction', 'data': transaction_data})
            logger.debug("Function call successful, circuit breaker state reset to CLOSED")
            return result
        except Exception as e:
            self.failures += 1
            transaction_data = {
                'transaction_id': "transaction_id",
                'user_id': 1,
                'payment_method': "POST",
                'status': 'failed',
                'initiated_at': datetime.datetime.now().isoformat(),
                'location': get_user_location("ip_address")
            }
            # Log the transaction failure
            send_log({'type': 'transaction', 'data': transaction_data})
            self.last_failure_time = time.time()
            logger.error("Function call failed: %s", e)
            logger.debug("Failure count increased to %d", self.failures)
            if self.failures >= self.failure_threshold:
                self.state = 'OPEN'
                logger.warning("Failure threshold reached. Transitioning to OPEN state")
            return CircuitBreakerError(e, "Function call failed within CircuitBreaker")

    def reset(self):
        self.failures = 0
        self.state = 'CLOSED'
        logger.debug("CircuitBreaker reset: state=CLOSED, failures=0")
