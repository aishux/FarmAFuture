from django.db import models
from django.contrib.auth.models import Group
# Create your models here.


class WebUser(models.Model):
    id = models.TextField(primary_key=True)
    full_name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)