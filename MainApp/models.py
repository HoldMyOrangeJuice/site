from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=30)
    amount = models.IntegerField()
    price = models.IntegerField()
    year = models.IntegerField()
    category = models.CharField(max_length=30)
    to_show = models.BooleanField(default=True)

