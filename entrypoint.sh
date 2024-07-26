#!/bin/sh

# Function to check for unapplied migrations
check_for_unapplied_migrations() {
    if [ -n "$(python manage.py showmigrations --plan | grep '\[ \]')" ]; then
        return 0  # There are unapplied migrations
    else
        return 1  # No unapplied migrations
    fi
}

# Check and apply migrations if there are any updates
if check_for_unapplied_migrations; then
    echo "Applying database migrations..."
    python manage.py migrate
else
    echo "No database migrations to apply."
fi

# Start Gunicorn server
exec gunicorn --bind 0.0.0.0:8004 payment_service.wsgi:application

