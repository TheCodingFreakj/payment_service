from django.apps import apps
from django.db import connection
class SchemaRouter:
    def db_for_read(self, model, **hints):
        return None

    def db_for_write(self, model, **hints):
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True

    def get_schema(self, model):
        return "user_schema"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        model = apps.get_model(app_label, model_name)
        schema = self.get_schema(model)
        if schema:
            with connection.cursor() as cursor:
                cursor.execute(f'SET search_path TO {schema}')
        return True
