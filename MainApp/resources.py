from import_export import resources
from .models import Item


class ItemRes(resources.ModelResource):
    class Meta:
        model = Item
