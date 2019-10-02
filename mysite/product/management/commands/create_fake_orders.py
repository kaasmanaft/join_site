import random
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User,Group
from product.models import Item
from Order.models import Order

class Command(BaseCommand):
    help = 'Create fake Users'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):

        super_user_list = User.objects.filter(username__iregex=r'su\d$').order_by('id')
        self.stdout.write(str(super_user_list))
        su1_users = User.objects.filter(groups__exact=super_user_list[0].groups.first())
        # self.stdout.write(str(su1))
        count = 0
        items_list = []
        while True:
            rand_item_pk = random.randint(9999, 999999)
            try:
                item = Item.objects.get(pk=rand_item_pk)
                count += 1
                items_list.append(item)
            except Item.DoesNotExist:
                pass
            if count > 20:
                self.stdout.write(str(items_list))
                break
        count = 0
        while count < 100:
            rand_item = random.choice(items_list)
            rand_user = random.choice(su1_users)
            rand_quantity = random.randint(1,3)
            order = Order(user=rand_user, item_id=rand_item,
                                         price=rand_item.price, quantity=rand_quantity)
            if order.is_valid():
                count += 1
                order.save()

        self.stdout.write(str(Order.objects.filter(user__in=su1_users)))