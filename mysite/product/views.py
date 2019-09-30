import time
from collections.abc import Iterable
from django.db import connection, reset_queries
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Item, Category, ItemCategory

parts_per_page_list = ['24', '48', '72']


def timer(func):
    def wraper(*args, **kwargs):
        import time
        start = time.time()
        res = func(*args, **kwargs)
        print(f'{func.__name__} -> {time.time() - start} sec')
        return res

    return wraper


def custom_paginator(page, part=100, number_items_on_page=24):
    page = int(page)
    if page <= 0:
        page = 1
    hundreds = page // part
    remainder = page % part
    if hundreds >= 1:
        paginator_correction = 3
        min_index = (hundreds * part - 3) * number_items_on_page
        max_index = ((hundreds + 1) * part + 3) * number_items_on_page
    else:
        paginator_correction = 0
        min_index = hundreds * part * number_items_on_page
        max_index = ((hundreds + 1) * part + 3) * number_items_on_page
    return {'hundreds': hundreds, 'remainder': remainder, 'paginator_correction': paginator_correction,
            'min_index': min_index, 'max_index': max_index}


def get_page_steps(item_pk):
    paginator = {'previousp': False, 'prev_3': False, 'prev_2': False, 'prev_1': False, 'page_content': None,
                 'last_id': None, 'first_id': None, 'next_1': False, 'next_2': False, 'next_3': False, 'nextp': False}
    pr = Item.objects.exclude(agg_photos__isnull=True).filter(pk__lt=item_pk).order_by('id')[:72].count()
    ne = Item.objects.exclude(agg_photos__isnull=True).filter(pk__gte=item_pk).order_by('id')[:72].count()
    if pr > 48:
        paginator['previousp'] = True
        paginator['prev_3'] = True
        paginator['prev_2'] = True
        paginator['prev_1'] = True
    elif pr > 24:
        paginator['previousp'] = True
        paginator['prev_3'] = False
        paginator['prev_2'] = True
        paginator['prev_1'] = True
    elif 0 < pr < 24:
        paginator['previousp'] = True
        paginator['prev_3'] = False
        paginator['prev_2'] = False
        paginator['prev_1'] = True

    if ne > 48:
        paginator['nextp'] = True
        paginator['next_3'] = True
        paginator['next_2'] = True
        paginator['next_1'] = True
    elif ne > 24:
        paginator['nextp'] = True
        paginator['next_3'] = False
        paginator['next_2'] = True
        paginator['next_1'] = True
    elif 0 < ne < 24:
        paginator['nextp'] = True
        paginator['next_3'] = False
        paginator['next_2'] = False
        paginator['next_1'] = True
    # print(f'pk {item_pk} ne {ne} pr {pr} {paginator}')
    return paginator


def custom_item_paginator(item_pk, step=None):
    search_word = ''
    if step == 'previousp':
        pr = Item.objects.exclude(agg_photos__isnull=True) \
                 .filter(pk__lt=item_pk, name__icontains=search_word).order_by('-id').values('id', 'name',
                                                                                             'base_photo_url',
                                                                                             'agg_photos', 'price',
                                                                                             'min_qty')[:24]
        first_id = pr[0]['id']
        last_id = pr[len(pr) - 1]['id']
        paginator = get_page_steps(last_id)
        paginator['page_content'] = pr
        paginator['first_id'] = first_id
        paginator['last_id'] = last_id

    elif step == 'nextp':
        pr = Item.objects.exclude(agg_photos__isnull=True) \
                 .filter(pk__gt=item_pk, name__icontains=search_word).order_by('id').values('id', 'name',
                                                                                            'base_photo_url',
                                                                                            'agg_photos', 'price',
                                                                                            'min_qty')[:24]
        first_id = pr[0]['id']
        last_id = pr[len(pr) - 1]['id']
        paginator = get_page_steps(last_id)
        paginator['page_content'] = pr
        paginator['first_id'] = first_id
        paginator['last_id'] = last_id

    else:
        pr = Item.objects.exclude(agg_photos__isnull=True) \
                 .filter(pk__gt=item_pk, name__icontains=search_word).order_by('id').values('id', 'name',
                                                                                            'base_photo_url',
                                                                                            'agg_photos', 'price',
                                                                                            'min_qty')[:24]
        paginator = get_page_steps(item_pk)
        first_id = pr[0]['id']
        last_id = pr[len(pr) - 1]['id']
        paginator['page_content'] = pr
        paginator['first_id'] = first_id
        paginator['last_id'] = last_id
    return paginator


# print(paginated_list[(page-1)*parts_per_page:page*parts_per_page])

def chunks(list, numbr_items_in_row, list_lenght):
    for i in range(0, list_lenght, numbr_items_in_row):
        yield list[i:i + numbr_items_in_row]


def get_query():
    for q in connection.queries:
        print(q)


@timer
def search_view(request):
    if request.method == 'GET':
        search_word = request.GET.get('search', None).lower()
        page = request.GET.get('page', 1)
        number_items_on_page = request.GET.get('items_on_page', 24)
        items = Item.objects.exclude(agg_photos__isnull=True).filter(name__contains=search_word).order_by('id') \
                    .values('id', 'agg_photos', 'base_photo_url', 'name', 'price', 'min_qty')
        breadcrumbs = ['Результаты поиска ' + search_word, ]
        menu = Category.objects.get_level(1).order_by('name')
        paginator = Paginator(items, number_items_on_page)
        current_page = paginator.get_page(page)
        cards = [n for n in chunks(current_page, 4, number_items_on_page)]
        context = {'menu': menu, 'cards': cards, 'page': current_page, 'breadcrumbs': breadcrumbs,
                   'search_word': search_word}
        return render(request, 'product/search_view.html', context=context)
    else:
        pass


@timer
def list_view(request, category_slug):
    if category_slug.lower() == 'top':
        if request.method == 'GET':
            breadcrumbs = None
            page = request.GET.get('page', 1)
            number_items_on_page = request.GET.get('items_on_page', 24)
            items = Item.objects.exclude(agg_photos__isnull=True).order_by('id') \
                        .values('id', 'agg_photos', 'base_photo_url', 'name', 'description')
            menu = Category.objects.get_level(1).order_by('name')
    else:
        page = request.GET.get('page', 1)
        number_items_on_page = request.GET.get('items_on_page', 24)
        category = Category.objects.get(slug=category_slug)
        breadcrumbs = category.get_bread_crumbs()
        descendants = Category.objects.get_descendants_id(category.id)
        if descendants.count() == 0:
            descendants = [category, ]
        items = Item.objects.filter(
            pk__in=ItemCategory.objects.filter(
                category_id__in=descendants).values('item_id')).exclude(agg_photos__isnull=True).order_by('id') \
                    .values('id', 'agg_photos', 'base_photo_url', 'name', 'description', 'price')
        menu = Category.objects.get_children(category.id).order_by('name')
    paginator = Paginator(items, number_items_on_page)
    current_page = paginator.get_page(page)
    cards = [n for n in chunks(current_page, 4, number_items_on_page)]
    context = {'menu': menu, 'cards': cards, 'page': current_page, 'breadcrumbs': breadcrumbs,}
    return render(request, 'product/category_view.html', context=context)


@timer
def list_view_tmp(request, category_slug):
    if category_slug.lower() == 'top':
        breadcrumbs = None
        items = Item.objects.all().exclude(agg_photos__isnull=True).order_by('id') \
            .values('id', 'agg_photos', 'base_photo_url', 'name', 'description')
        menu = Category.objects.get_level(1).order_by('name')
    else:
        category = Category.objects.get(slug=category_slug)
        breadcrumbs = category.get_bread_crumbs()
        descendants = Category.objects.get_descendants_id(category.id)
        if descendants.count() == 0:
            descendants = [category, ]
        items = Item.objects.filter(
            pk__in=ItemCategory.objects.filter(
                category_id__in=descendants).values('item_id')).exclude(agg_photos__isnull=True).order_by('id') \
                    .values('id', 'agg_photos', 'base_photo_url', 'name', 'description', 'price')[3000:4000]
        menu = Category.objects.get_children(category.id).order_by('name')
    page = request.GET.get('page', 1)
    number_items_on_page = request.GET.get('items_on_page', '24')
    paginator = Paginator(items, page, number_items_on_page)
    items_page = paginator.page(page)
    cards = [n for n in chunks(items_page, 4)]
    context = {'menu': menu, 'product': cards, 'breadcrumbs': breadcrumbs}
    return render(request, 'product/category_view.html', context=context)


def product_view(request, product_id=None):
    if product_id is None:
        return redirect('top')
    else:
        item = Item.objects.get(pk=product_id)
        print(f'item category {ItemCategory.objects.filter(item_id__exact=item.id)}')
        print(f'item category {item}')
        item_category = ItemCategory.objects.filter(item_id__exact=item.id).first().category_id

        category = Category.objects.get(pk=item_category.id)
        breadcrumbs = category.get_bread_crumbs()
        menu = Category.objects.get_level(1).order_by('name')
    context = {'menu': menu, 'card': item, 'breadcrumbs': breadcrumbs}
    return render(request, 'product/product_view.html', context=context)
