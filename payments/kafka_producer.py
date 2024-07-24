import queue
import threading
from kafka import KafkaProducer
from django.conf import settings
import ssl
import json

class KafkaProducerPool:
    def __init__(self, pool_size=5):
        self.pool_size = pool_size
        self.pool = queue.Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        self._initialize_pool()

    def _initialize_pool(self):
        context = ssl.create_default_context()
        context.load_verify_locations(settings.KAFKA_CA_CERT)
        context.load_cert_chain(certfile=settings.KAFKA_CLIENT_CERT, keyfile=settings.KAFKA_CLIENT_KEY)

        for _ in range(self.pool_size):
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BROKER_URLS,
                security_protocol='SSL',
                ssl_context=context,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=5,
                request_timeout_ms=30000,
                retry_backoff_ms=500,
                linger_ms=10
            )
            self.pool.put(producer)

    def get_producer(self):
        with self.lock:
            return self.pool.get()

    def return_producer(self, producer):
        with self.lock:
            self.pool.put(producer)

    def send_message(self, topic, value):
        producer = self.get_producer()
        try:
            producer.send(topic, value)
            producer.flush()
        finally:
            self.return_producer(producer)
