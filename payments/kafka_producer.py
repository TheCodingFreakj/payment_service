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
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
            # sasl_mechanism = 'SCRAM-SHA-256',
            # sasl_plain_username=settings.KAFKA_USERNAME,
            # sasl_plain_password=settings.KAFKA_PASSWORD,
            # security_protocol="SASL_SSL",
            # ssl_cafile=settings.KAFKA_CA_CERT,
            #value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    def send_message(self, topic, value):
        self.producer.send(topic, value)
        self.producer.flush()
