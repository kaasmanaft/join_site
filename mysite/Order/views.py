from typing import List, Dict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order
from product.models import Item, Category,ItemCategory
from django.db.models import Sum
from django.contrib import messages
from django.core.paginator import Paginator

def dictfetchall(cursor) -> List:
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
          ]

#
# def get_description_by_id(it: int) -> List:
#     return Item.objects.get(pk=it)
#

def total_number_orders_by_id(itemid , user) :
    count = Order.objects.filter(item_id__exact=itemid, user__groups__exact=user.groups.first())\
        .aggregate(total_order_quantity=Sum('quantity'))#, user__groups__contains=user.groups.first())#.annotate(cun=Count('item_id'))
    return count['total_order_quantity']


def db_goods_view_tmp(request, limit=10):
    if request.method == "POST":
        return redirect('customers')
    else:

        if 'page_limit' in request.GET.dict():
            page_limit = request.GET.dict()['page_limit']
        else:
            page_limit = 10
        try:
            category_id = request.GET.dict()['category_id']
        except KeyError:
            category_id = 0
        try:
            page = request.GET.get('page')
        except KeyError:
            page = 1
        if category_id:
            children = Category.objects.get_children(category_id).values('id', 'name', 'slug')
            descendants = Category.objects.get_descendants_id(category_id)
            # print(children)
            # print(f'descendants len {len(descendants)}   {descendants} category_id is {category_id}')
            items_in_category = ItemCategory.objects.all().filter(category_id__in=descendants).values_list('item_id', flat=True)
            dbd = Item.objects.all().filter(pk__in=items_in_category).order_by('id')
            # print(f'items_in_category len {len(items_in_category)}   {items_in_category} category_id is {category_id}')
        else:
            children = Category.objects.get_level(1).values('id', 'name', 'slug')
            # print(children)
            dbd = Item.objects.all().exclude(agg_photos__isnull=True, balance='0', price__lte=0.0).order_by('-price')[
                   0:limit]

        paginator = Paginator(dbd, page_limit)
        obj = paginator.get_page(page)
        context = {'obj': obj, 'quantity': 1, 'menu': children}
        return render(request, template_name='Order/db.html', context=context)




@login_required()
def show_user_orders(request):
    orders = Order.objects.filter(user__username__exact=request.user).values_list('item_id', 'quantity')
    order_list = []
    print(f'orders type id {type(orders)}')
    order_description = {}
    for item_id, user_order_quantity in orders:

        total_order_quantity = total_number_orders_by_id(item_id, request.user)
        order = Item.objects.get(pk=item_id)
        order.order_description = {'total': total_order_quantity, 'user': user_order_quantity}
        order_list.append(order)
    context = {'orders': order_list}
    print(context)
    return render(request, template_name='Order/user_page.html', context=context)

@login_required()
def save_order(request):
    print(request.POST)
    if request.method == "POST":
        item = int(request.POST['id'])
        quantity = int(request.POST['quantity'])
        try:
            order = Order.objects.get(item_id__exact=item, user__username__exact=request.user)
            if quantity > 0:
                order.quantity = order.quantity + quantity
                messages.add_message(request, messages.SUCCESS, "Order has been updated")
                order.save()
                print(order)
            else:
                messages.add_message(request, messages.ERROR, "Wrong number of goods")

        except Order.DoesNotExist:
            print('There is no any orders with that ID')
            new_order = Order()
            item_id = int(request.POST['id'])
            quantity = request.POST['quantity']
            new_order.item_id = item_id
            item_info = Item.objects.get(pk=item_id)
            new_order.user = request.user
            new_order.quantity = quantity
            new_order.price = item_info.price
            new_order.is_partner_goods = item_info.is_remote_store
            if new_order.is_valid():
                new_order.save()
                return redirect('top')
            else:
                print(repr(new_order))
                return redirect('item', new_order.item_id)
        return redirect('item', item)
    else:
        return redirect('top')


@login_required()
def delete_order(request):
    pass


def show_goods_by_id(request, item_id=0):
    obj = get_object_or_404(Item, pk=item_id)
    context = {'obj': obj}
    if request.user:
        try:
            order = Order.objects.get(item_id__exact=int(item_id), user__username__exact=request.user)
            context = {'obj': obj, 'user_order_quantity': order.quantity}
        except Order.DoesNotExist:
            context = {'obj': obj, 'quantity': 1}

    return render(request, template_name='Order/item.html', context=context)
