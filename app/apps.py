from django.apps import AppConfig
from django.dispatch import receiver
from djangochannelsrestframework.signals import post_bulk_save
class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self) -> None:

        from .models import Post, Temp
        @receiver(post_bulk_save, sender=Post)
        def señal(sender, instance, **kwargs):
            Temp.objects.create(fk=instance, name=instance.name)

        return super().ready()