from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CASCADE

"""
Custom user model used by Django
"""


class Customer(AbstractUser):
    phone = models.CharField(blank=False, max_length=18)
    is_confirmed = models.BooleanField(default=False)
    is_subbed_to_mailing = models.BooleanField(default=False)


"""
Temporary user based on session cookie
"""


class TempUser(models.Model):
    username = models.TextField(blank=False)
    email = models.EmailField(blank=True)
    phone = models.CharField(blank=False, max_length=18)


class Item(models.Model):
    name = models.TextField(blank=True, null=None, default=None)
    name_to_search = models.TextField(blank=True, null=None)
    amount = models.IntegerField(blank=True, null=None)
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
    description = models.TextField(default=" - ", blank=True)
    last_edited = models.DateField(auto_now_add=True, blank=True)


class ItemPage(models.Model):
    item_name = models.TextField(blank=False)
    index = models.IntegerField(blank=True, null=None, unique=True)


class Order(models.Model):
    customer = models.ForeignKey(Customer, CASCADE)
    temp_user = models.ForeignKey(TempUser, CASCADE)
    customer_is_logged_in = models.BooleanField(blank=False)

    item_name = models.TextField(blank=False)
    item_id = models.IntegerField(blank=False)
    item_amount = models.IntegerField(blank=False)

    day = models.DateField(auto_now_add=True, blank=True)
    time = models.TimeField(auto_now_add=True, blank=True)

    seen = models.BooleanField(default=False)

    def get_customer(self):
        if self.customer_is_logged_in:
            return self.customer
        elif self.customer:
            return self.temp_user

    @staticmethod
    def get_user_orders(customer):
        if isinstance(customer, Customer):
            return Order.objects.all().filter(customer=customer)

        return Order.objects.all().filter(temp_user=customer)










