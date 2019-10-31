from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.utils import timezone
from product.models import Item


class Order(models.Model):
    order_status = [
        ('ACT', 'active'),
        ('INACT', 'inactive'),
        ('PAID', 'paid'),
        ('DELIV', 'delivery'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    group_order = models.ForeignKey('GroupOrder', on_delete=models.CASCADE, null=True)
    price = models.FloatField()
    total_price = models.FloatField(null=True)
    quantity = models.PositiveIntegerField()
    status = models.CharField(choices=order_status, default='ACT', max_length=5)
    order_date = models.DateField(default=timezone.now)
    delivery_date = models.DateField(null=True)
    is_partner_goods = models.BooleanField(default=False)
    class Meta:
        ordering = ['user',]
    def is_valid(self):
        if int(self.price) <= 0:
            print(f'wrong price {self.price}')
            return False
        if int(self.quantity) <= 0:
            print('quantity is wrong')
            return False
        if not isinstance(self.item_id, Item):
            print(f'Something wrong with id {self.item_id} {self.price} {self.user}')
            return False
        if self.user is None:
            print('Some thing wrong with user')
            return False
        self.create_or_set_group_order()
        return True

    def create_or_set_group_order(self):
        try:
            go = GroupOrder.objects.get(item=self.item_id)
            go.total_quantity = go.total_quantity + self.quantity
        except GroupOrder.DoesNotExist:
            go = GroupOrder.objects.create(owner=self.user.groups.first(), item=self.item_id, total_quantity=self.quantity)
        go.save()
        self.group_order = go
        return True

    def save(self):
        self.total_price = round(self.quantity * self.price,2)
        super(Order, self).save()


class GroupOrder(models.Model):
    owner = models.ForeignKey(Group, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    total_quantity = models.PositiveSmallIntegerField(default=0)
    

    def get_total_quantity(self):
        total_quantity = Order.objects.filter(user__groups__exact=self.owner, item_id=self.item).aggregate(summ=Sum('quantity'))
        self.total_quantity = total_quantity['summ']
    def __str__(self):
        return str(self.item.name) + '\t' +str(self.total_quantity)