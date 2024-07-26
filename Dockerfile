# Base image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Copy project
COPY . /code/


# Copy entrypoint script
COPY entrypoint.sh /code/entrypoint.sh

# Make the script executable
RUN chmod +x /code/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]
# # Command to run the server
# CMD ["gunicorn", "--bind", "0.0.0.0:8004", "payment_service.wsgi:application"]