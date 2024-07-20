# logging_config.py

import logging

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set this to the desired level for your application

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # Set this to the desired level for your application

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add formatter to ch
ch.setFormatter(formatter)

# Add ch to logger
logger.addHandler(ch)

# Suppress RabbitMQ (pika) library logs
logging.getLogger('pika').setLevel(logging.WARNING)  # Suppress pika logs lower than WARNING
