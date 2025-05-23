from django.apps import AppConfig


class BasesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bases'

    def ready(self):
        import bases.signals

