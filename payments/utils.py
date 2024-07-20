import logging
import time

# Configure the logging
logging.basicConfig(level=logging.info)
logger = logging.getLogger(__name__)

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_time=60):
        self.failure_threshold = failure_threshold
        self.recovery_time = recovery_time
        self.failures = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'
        logger.info("Initialized CircuitBreaker with failure_threshold=%d, recovery_time=%d", failure_threshold, recovery_time)

    def call(self, func, *args, **kwargs):
        logger.info("CircuitBreaker call: state=%s, failures=%d", self.state, self.failures)
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_time:
                self.state = 'HALF-OPEN'
                logger.info("Transitioning to HALF-OPEN state")
            else:
                logger.warning("Circuit breaker is open. Cannot call function.")
                raise Exception('Circuit breaker is open')

        try:
            result = func(*args, **kwargs)
            self.reset()
            logger.info(f"Function call successful, {result}")
            logger.info("Function call successful, circuit breaker state reset to CLOSED")
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            logger.error("Function call failed: %s", e)
            logger.info("Failure count increased to %d", self.failures)
            if self.failures >= self.failure_threshold:
                self.state = 'OPEN'
                logger.warning("Failure threshold reached. Transitioning to OPEN state")
            raise e

    def reset(self):
        self.failures = 0
        self.state = 'CLOSED'
        logger.info("CircuitBreaker reset: state=CLOSED, failures=0")
