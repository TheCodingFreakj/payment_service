from kafka import KafkaProducer
from django.conf import settings
import ssl
import json

class KafkaProducerService:
    def __init__(self):
        context = ssl.create_default_context()
        context.load_verify_locations(settings.KAFKA_CA_CERT)
        context.load_cert_chain(certfile=settings.KAFKA_CLIENT_CERT, keyfile=settings.KAFKA_CLIENT_KEY)

        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER_URLS,
            security_protocol='SSL',
            ssl_context=context,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=5,
            enable_idempotence=True,
            request_timeout_ms=30000,  # Request timeout
            delivery_timeout_ms=30000  # Delivery timeout
        )
    def send_message(self, topic, value):
        self.producer.send(topic, value)
        self.producer.flush()
