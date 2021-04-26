from django.db import models
from djangochannelsrestframework.managers import CustomManager
# Create your models here.

class Post(models.Model):
    name = models.CharField(max_length=50)

    objects = CustomManager()


class Temp(models.Model):
    fk = models.ForeignKey(Post, related_name="temps", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)