from django.apps import AppConfig


class QsystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'qsystem'
    
    def ready(self):
        import qsystem.signals
