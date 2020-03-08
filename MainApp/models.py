from django.db import models


class Item(models.Model):
    name = models.TextField(blank=True, null=None, default=None)
    name_to_search = models.TextField(blank=True, null=None)
    amount = models.TextField(blank=True, null=None)
    price = models.TextField(blank=True, null=None)
    year = models.TextField(blank=True, null=None)
    category = models.TextField(blank=True, null=None)
    category_to_search = models.TextField(blank=True, null=None)
    is_hidden = models.BooleanField(blank=True, null=None)
    photo_link = models.TextField(blank=True, null=None)
    spot = models.TextField(blank=True, null=None)
    sum = models.TextField(blank=True, null=None)
    notes = models.TextField(blank=True, null=None)
    index = models.IntegerField(blank=True, null=None, unique=True)
    description = models.TextField(default="defaultr dest test", blank=True)


class ItemPage(models.Model):
    item_name = models.TextField(blank=False)
    index = models.IntegerField(blank=True, null=None, unique=True)

