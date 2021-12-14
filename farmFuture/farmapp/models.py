from django.db import models
from django.contrib.auth.models import Group
# Create your models here.


class WebUser(models.Model):
    id = models.TextField(primary_key=True)
    full_name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    request_farmer = models.BooleanField(default=False)
    farmer_id = models.CharField(max_length=200, default="", null=True, blank=True)
    aadhaar_link = models.URLField(default="", null=True, blank=True)
    account_address = models.CharField(max_length=50, default="", null=True, blank=True)

    def __str__(self):
        return self.full_name + "(" + str(self.group) + ")"


class Orders(models.Model):
    user = models.ForeignKey(WebUser, default=1, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, primary_key=True)
    items_json = models.CharField(max_length=5000)
    amount = models.FloatField(default=0)
    name = models.CharField(max_length=90)
    email = models.CharField(max_length=111)
    address = models.CharField(max_length=111)
    city = models.CharField(max_length=111)
    state = models.CharField(max_length=111)
    zip_code = models.CharField(max_length=111)
    phone = models.CharField(max_length=111, default="")

    def __str__(self):
        return self.name+"(id:"+str(self.order_id)+")"


class Cart(models.Model):
    user = models.ForeignKey(WebUser, on_delete=models.CASCADE)
    cart = models.TextField(null=True, blank=True)