import pika
import json
import logging
from datetime import datetime

import requests

from .loggin_config import logger

def send_log(log_data):
    try:
        url = 'amqps://qszdxpbw:7H0HtHw6-gPkGC8KoIW-wHqUwTlaVzbp@cow.rmq2.cloudamqp.com/qszdxpbw'
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='logs')
        channel.basic_publish(exchange='', routing_key='logs', body=json.dumps(log_data))
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Connection error while sending log message: {e}")
    except pika.exceptions.ProbableAuthenticationError as e:
        logger.error(f"Authentication error while sending log message: {e}")
    except Exception as e:
        logger.error(f"Error sending log message: {e}")

def get_user_location(ip_address):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip_address}')
        data = response.json()
        return f"{data['city']}, {data['country']}"
    except Exception as e:
        logger.error(f"Error fetching user location: {e}")
        return "Unknown"        