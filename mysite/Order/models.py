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
    quantity = models.IntegerField()
    status = models.CharField(choices=order_status, default='ACT', max_length=5)
    order_date = models.DateField(default=timezone.now)
    delivery_date = models.DateField(null=True)
    is_partner_goods = models.BooleanField(default=False)



