from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


order_status = [
    ('ACT','active'),
    ('INACT','inactive'),
    ('PAID','paid'),
    ('DELIV','delivery'),
]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_id = models.PositiveIntegerField(null=True)
    price = models.FloatField()
    quantity = models.PositiveIntegerField()
    status = models.CharField(choices=order_status, default='ACT', max_length=5)
    order_date = models.DateField(default=timezone.now)
    delivery_date = models.DateField(null=True)
    is_partner_goods = models.BooleanField(default=False)

    def is_valid(self):
        if int(self.price) <= 0:
            return False
        if int(self.quantity) <= 0:
            return False
        if int(self.item_id) <= 0:
            return False
        if self.user is None:
            return False
        return True



