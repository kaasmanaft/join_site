import time
from collections.abc import Iterable
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


def custom_paginator(page, part=100):
    page = int(page)
    if page <= 0:
        page = 1
    hundreds = page//part
    remainder = page % part
    if hundreds >= 1:
        paginator_correction = 3
        min_index = hundreds*part-3
        max_index = (hundreds+1)*part+3
    else:
        paginator_correction = 0
        min_index = hundreds*part
        max_index = (hundreds+1)*part+3
    return {'hundreds': hundreds, 'remainder': remainder, 'paginator_correction': paginator_correction,
            'min_index': min_index, 'max_index': max_index}




def get_page_steps(item_pk):
    paginator = {'previousp': False, 'prev_3': False, 'prev_2': False, 'prev_1': False, 'page_content':None,
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
    if step =='previousp':
        pr = Item.objects.exclude(agg_photos__isnull=True)\
                 .filter(pk__lt=item_pk, name__icontains=search_word).order_by('-id').values('id','name','base_photo_url',
                                                                'agg_photos','price', 'min_qty')[:24]
        first_id = pr[0]['id']
        last_id = pr[len(pr)-1]['id']
        paginator = get_page_steps(last_id)
        paginator['page_content'] = pr
        paginator['first_id'] = first_id
        paginator['last_id'] = last_id

    elif step =='nextp':
        pr = Item.objects.exclude(agg_photos__isnull=True)\
                 .filter(pk__gt=item_pk, name__icontains=search_word).order_by('id').values('id','name','base_photo_url',
                                                                'agg_photos','price', 'min_qty')[:24]
        first_id = pr[0]['id']
        last_id = pr[len(pr)-1]['id']
        paginator = get_page_steps(last_id)
        paginator['page_content'] = pr
        paginator['first_id'] = first_id
        paginator['last_id'] = last_id

    else:
        pr = Item.objects.exclude(agg_photos__isnull=True)\
                 .filter(pk__gt=item_pk,name__icontains=search_word).order_by('id').values('id','name','base_photo_url',
                                                                'agg_photos','price', 'min_qty')[:24]
        paginator = get_page_steps(item_pk)
        first_id = pr[0]['id']
        last_id = pr[len(pr)-1]['id']
        paginator['page_content'] = pr
        paginator['first_id'] = first_id
        paginator['last_id'] = last_id
    return paginator


# print(paginated_list[(page-1)*parts_per_page:page*parts_per_page])

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def search_view(request):
    if request.method == 'GET':
        search_word = request.GET.get('search', None)
        page = request.GET.get('page', 1)
        number_items_on_page = request.GET.get('items_on_page', 24)

        items = Item.objects.all().exclude(agg_photos__isnull=True) \
            .filter(name__icontains=str(search_word)).order_by('name')
        breadcrumbs = ['Результаты поиска ' + search_word, ]
        menu = Category.objects.get_level(1).order_by('name')
        paginator = Paginator(items, number_items_on_page)
        items_page = paginator.get_page(page)
        context = {'menu': menu,
                   'items': list(chunks(items_page, 4)),
                   'page': items_page,
                   'breadcrumbs': breadcrumbs,
                   'search': search_word
                   }
        return render(request, 'product/search_view.html', context=context)
    else:
        pass


@timer
def list_view(request, category_slug):
    start = time.time()
    if category_slug.lower() == 'top':
        if request.method == 'GET':
            breadcrumbs = None
            page = request.GET.get('page', 1)
            paginator_slice = custom_paginator(page)
            print(page)
            items = Item.objects.exclude(agg_photos__isnull=True).order_by('id') \
                .values('id', 'agg_photos', 'base_photo_url', 'name', 'description')[paginator_slice['min_index']:
                                                                                     paginator_slice['max_index']]

            print(f'{paginator_slice["min_index"]}  {paginator_slice["max_index"]}')
            menu = Category.objects.get_level(1).order_by('name')
            print(time.time() - start)
    else:
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
    # page = request.GET.get('page', 1)

    number_items_on_page = request.GET.get('items_on_page', 24)

    paginator = Paginator(items, number_items_on_page)
    print(f'-{page}')
    start = time.time()
    if paginator_slice['hundreds']:
        curent_page = paginator.get_page((int(page)+3)//paginator_slice['hundreds'])
    else:
        curent_page = paginator.get_page(int(page))
    print(time.time() - start)
    # print(f'page is {page} slice is [{paginator_slice["min_index"]} : {paginator_slice["max_index"]}] page in paginator'
    #       f' is {(int(page)+3)//paginator_slice["hundreds"]}')
    start = time.time()
    cards = [n for n in chunks(curent_page, 4)]
    print(time.time() - start)
    context = {'menu': menu, 'cards': cards, 'page': curent_page, 'breadcrumbs': breadcrumbs}
    return render(request, 'product/ts_view.html', context=context)


@timer
def list_view_tmp(request, category_slug):
    if category_slug.lower() == 'top':
        start = time.time()
        breadcrumbs = None
        items = Item.objects.all().exclude(agg_photos__isnull=True).order_by('name') \
                    .values('id', 'agg_photos', 'base_photo_url', 'name', 'description')[:200]
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

    paginator = custom_paginator(items, page, number_items_on_page)

    items_page = items[paginator['slice_min']:paginator['slice_max']]

    cards = [n for n in chunks(items_page, 4)]
    context = {'menu': menu, 'product': cards, 'page': page, 'breadcrumbs': breadcrumbs}
    return render(request, 'product/ts_view.html', context=context)


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
