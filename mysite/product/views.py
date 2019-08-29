from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from .models import Item, Category, ItemCategory


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def category_view(request, category_slug):
    if category_slug.lower() == 'top':
        menu = Category.objects.get_level(1).order_by('name')
        breadcrumbs = None
        items = Item.objects.all().exclude(agg_photos__isnull=True).order_by('name')[:120]
    else:
        category = Category.objects.get(slug=category_slug)
        breadcrumbs = category.get_bread_crumbs()
        descendants = Category.objects.get_descendants_id(category.id)
        if descendants.count() == 0:
            descendants = [category, ]
        items = Item.objects.filter(
            pk__in=ItemCategory.objects.filter(
                category_id__in=descendants).values('item_id')).exclude(agg_photos__isnull=True).order_by('id')
        menu = Category.objects.get_children(category.id).order_by('name')
    page = request.GET.get('page', 1)
    number_items_on_page = request.GET.get('items_on_page', 24)
    paginator = Paginator(items, number_items_on_page)
    items_page = paginator.get_page(page)

    context = {'menu': menu, 'items': list(chunks(items_page, 4)), 'page': items_page, 'breadcrumbs':breadcrumbs}
    return render(request, 'product/category_view.html', context=context)


def product_view(request, product_id=None):
    if product_id is None:
        return redirect('top')
    else:
        item = Item.objects.get(pk=product_id)
        item_category = ItemCategory.objects.filter(item_id__exact=item.id).first().category_id
        category = Category.objects.get(pk=item_category.id)
        breadcrumbs = category.get_bread_crumbs()
        menu = Category.objects.get_level(1).order_by('name')
    context = {'menu': menu, 'card': item, 'breadcrumbs': breadcrumbs}
    return render(request, 'product/product_view.html', context=context)
