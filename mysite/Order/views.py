from typing import List, Dict
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from .models import Order, GroupOrder
from product.models import Item, Category,ItemCategory
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator
from product.views import chunks, get_query, timer

def dictfetchall(cursor) -> List:
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
          ]




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
            items_in_category = ItemCategory.objects.all().filter(category_id__in=descendants).values_list('item_id', flat=True)
            dbd = Item.objects.all().filter(pk__in=items_in_category).order_by('id')
        else:
            children = Category.objects.get_level(1).values('id', 'name', 'slug')
            dbd = Item.objects.all().exclude(agg_photos__isnull=True, balance='0', price__lte=0.0).order_by('-price')[
                   0:limit]
        paginator = Paginator(dbd, page_limit)
        obj = paginator.get_page(page)
        context = {'obj': obj, 'quantity': 1, 'menu': children}
        return render(request, template_name='Order/db.html', context=context)

#
# @login_required()
# def show_group_orders(request):
#     if request.user.has_perm('Order.view_grouporder'):
#         group_name = request.user.groups.first()
#         group = get_object_or_404(Group, name=group_name)
#         group_orders = GroupOrder.objects.filter(owner=group).select_related('item')
#         orders_list = []
#         summ = 0
#         for group_order in group_orders:
#             total_price = round(group_order.item.price*group_order.total_quantity,2)
#             orders = Order.objects.filter(user__groups__exact=group_name, item_id=group_order.item_id).select_related('user')
#             summ += total_price
#             orders_list.append([group_order, total_price, orders])
#         context = {'group_orders': orders_list, 'summ': round(summ, 2), 'action_list': Order.order_status}
#         return render(request, template_name='Order/group_page.html', context=context)
#
#     else:
#         return redirect('top')
#
@timer
@login_required()
def show_group_orders(request):
    if request.user.has_perm('Order.view_grouporder'):
        group_name = request.user.groups.first()
        group = get_object_or_404(Group, name=group_name)
        orders = Order.objects.filter(user__groups__exact=group_name).order_by('user')\
            .values_list('item_id', 'user__username', 'status', 'quantity','id', 'order_date', 'delivery_date','total_price')
        group_orders = GroupOrder.objects.filter(owner=group).order_by('owner')\
            .values('item_id', 'item_id__name','item_id__price','item_id__min_qty','total_quantity')
        orders_dict = {}
        for order in orders:
            try:
                orders_dict[order[0]].append(order[1:])
            except KeyError:
                orders_dict[order[0]] = [order[1:]]
        for order_group in group_orders:
            order_group['orders'] = orders_dict[order_group['item_id']]
        action = Order.order_status+[('DEL', 'delete')]
        context = {'group_orders': group_orders, 'action_list': action}
        return render(request, template_name='Order/group_page_tmp.html', context=context)

    else:
        return redirect('top')


@login_required()
def update_orders(request):
    if request.method == 'POST':
        if request.user.has_perm('Order.change_grouporder') and request.user.has_perm('Order.change_order'):
            print('------------------------------------------------')
            print(request.POST)
            update_list = []
            for key in request.POST.keys():
                if request.POST[key] == 'on':
                    update_list.append(key)
            if request.POST['act'] == 'DELIV':
                try:
                    delivery_date = datetime.datetime.strptime(request.POST['delivery_date'], '%Y-%m-%d')
                except ValueError:
                    text = 'Неверная дата доставки. \n Укажите дату доставки.'
                    messages.add_message(request,messages.ERROR,text)
                    return redirect('group_order')
                if delivery_date <= datetime.datetime.now():
                    text = 'Неверная дата доставки. \n Доставка не может быть в прошлом.'
                    messages.add_message(request,messages.ERROR,text)
                    return redirect('group_order')

                Order.objects.filter(id__in=update_list).update(status=request.POST['act'], delivery_date=request.POST['delivery_date'])
                text = 'Дата доставки установлена успешно'
                messages.add_message(request, messages.SUCCESS, text)
                return redirect('group_order')
            elif request.POST['act'] == 'DEL':
                try:
                    Order.objects.filter(id__in=update_list).delete()
                except :
                    text = 'Неверная дата доставки. \n Доставка не может быть в прошлом.'
                    messages.add_message(request,messages.ERROR,text)
                    return redirect('group_order')
                text = 'Ордера успешно удалены.'
                messages.add_message(request,messages.SUCCESS,text)
            else:
                try:
                    Order.objects.filter(id__in=update_list).update(status=request.POST['act'])
                except:
                    text = 'Во время обновления ордеров что-то пошло не так '
                    messages.add_message(request,messages.ERROR,text)
                    return redirect('group_order')
                text = 'Ордера обновлены успешно.'
                messages.add_message(request,messages.SUCCESS,text)
            return redirect('group_order')
        else:
            return redirect('top')
    else:
        return redirect('top')


@login_required()
def show_user_orders(request):
    orders = Order.objects.filter(user=request.user).select_related('item_id', 'group_order')
    orders = chunks(orders, 4, len(orders))
    context = {'user_orders': orders}
    return render(request, template_name='Order/user_page.html', context=context)

#
# @login_required()
# def show_user_orders(request):
#     orders = Order.objects.filter(user__username__exact=request.user).values_list('item_id', 'quantity')
#     # orders = Order.objects.filter(user__username__exact=request.user).values_list('item_id', 'quantity')
#     get_query()
#     print(f'order len {len(orders)} {orders.values_list}')
#     order_list = []
#     order_description = {}
#     for item_id, user_order_quantity in orders:
#      orders_M1 = Order.objects.filter(user__groups__exact = m1.groups.first()).select_related('item_id')

#         total_order_quantity = total_number_orders_by_id(item_id, request.user)
#         order = Item.objects.get(pk=item_id)
#         order.order_description = {'total': total_order_quantity, 'user': user_order_quantity}
#         order_list.append(order)
#     order_list = chunks(order_list, 4, len(order_list))
#     context = {'orders': order_list}
#     print(context)
#     return render(request, template_name='Order/user_page.html', context=context)
#

@login_required()
def save_order(request):
    print(request.POST)
    if request.method == "POST":
        item = Item.objects.get(pk=int(request.POST['id']))
        quantity = int(request.POST['quantity'])
        try:
            order = Order.objects.get(item_id=item, user__username=request.user)
            if quantity > 0:
                order.quantity = order.quantity + quantity
                messages.add_message(request, messages.SUCCESS, "Order has been updated")
                order.save()
                gr_ord = order.group_order
                gr_ord.get_total_quantity()
                gr_ord.save()
                print(order)
            else:
                messages.add_message(request, messages.ERROR, "Wrong number of goods")

        except Order.DoesNotExist:
            new_order = Order()
            new_order.item_id = item
            new_order.user = request.user
            new_order.quantity = quantity
            new_order.price = item.price
            new_order.is_partner_goods = item.is_remote_store
            if new_order.is_valid():
                new_order.save()
                return redirect('top')
            else:
                return redirect('item', new_order.item_id_id)
        return redirect('item', item.id)
    else:
        return redirect('top')

@login_required()
def update_order(request):
    if request.method == "POST":
        item = int(request.POST['id'])
        quantity = int(request.POST['quantity'])
        try:
            order = Order.objects.get(item_id__exact=Item.objects.get(pk=item), user__username__exact=request.user)
            if quantity > 0:
                order.quantity = order.quantity + quantity
                messages.add_message(request, messages.SUCCESS, "Order has been updated")
                order.save()
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
