from django.db import models


class Item(models.Model):
    name = models.TextField(blank=True, null=None)
    amount = models.TextField(blank=True, null=None)
    price = models.TextField(blank=True, null=None)
    year = models.TextField(blank=True, null=None)
    category = models.TextField(blank=True, null=None)
    to_show = models.BooleanField(blank=True, null=None)

