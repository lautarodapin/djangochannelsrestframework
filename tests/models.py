from django.db import models
from djangochannelsrestframework.signals import post_bulk_save
from django.dispatch import receiver
from djangochannelsrestframework.managers import CustomManager
class TestModel(models.Model):
    """Simple model to test with."""

    name = models.CharField(max_length=255)

    objects = CustomManager()

