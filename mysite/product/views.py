from django.db import connection
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
        context = {'menu': menu, 'page': current_page, 'breadcrumbs': breadcrumbs,'search_word': search_word}
        return render(request, 'product/search_view.html', context=context)
    else:
        return redirect('top')


@timer
def list_view(request, category_slug):
    if request.method == 'GET':
        if category_slug.lower() == 'top':
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
        context = {'menu': menu, 'page': current_page, 'breadcrumbs': breadcrumbs,}
        return render(request, 'product/category_view.html', context=context)
    else:
        return redirect('top')




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
    context = {'menu': menu, 'product': items_page, 'breadcrumbs': breadcrumbs}
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
