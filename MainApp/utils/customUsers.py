from MainApp.models import Order


class TempUser:
    def __init__(self, id):
        self.uuid = id

    def get_orders(self):
        return Order.objects.all().filter(customer_id=self.uuid)

    def get_id(self):
        return self.uuid


class LoggedInUser:
    def __init__(self, id):
        self.id = id

    def get_orders(self):
        return Order.objects.all().filter(customer_id=self.id)

    def get_id(self):
        return self.id


