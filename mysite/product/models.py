import os
import yaml
from anytree import Node, RenderTree
from anytree.exporter import DictExporter
from anytree.importer import DictImporter
from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


class Item(models.Model):
    agg_photos = ArrayField(models.PositiveSmallIntegerField(), null=True)  # Индексы    фотографий,
    balance = models.CharField(max_length=100,default='')  # Баланс на    складе.
    barcodes = ArrayField(models.CharField(max_length=20), null=True)   # Штрих - коды,
    base_photo_url = models.CharField(max_length=1024)  # Базовый    url    фотографий,
    box_depth = models.FloatField()  # Глубина    упаковки    в    см.,
    box_height = models.FloatField()  # Высота    упаковки    в    см.,
    box_width = models.FloatField()  # Ширина    упаковки    в    см.,
    country_id = models.ForeignKey('Country', on_delete=models.DO_NOTHING)  # Идентификатор    страны    производителя,
    depth = models.FloatField()  # Глубина    в    см.,
    description = models.TextField(null=True)  # Описание,
    height = models.FloatField()  # Высота    в    см.,
    id = models.PositiveIntegerField(primary_key=True)  # Идентификатор,
    is_adult = models.BooleanField()  # Товар    18 +,
    is_markdown = models.BooleanField()  # Уцененный    товар,
    is_paid_delivery = models.BooleanField()  # Платная    доставка,
    is_price_fixed = models.BooleanField()  # Фиксированная    цена,
    is_remote_store= models.BooleanField()  # Товар    является    товаром    партнера,
    min_qty = models.PositiveSmallIntegerField()  # Минимальное    количество    в    заказе,
    minimum_order_quantity = models.FloatField()  # УСТАРЕВШЕЕ.Минимальное    количество    в    заказе,
    name = models.CharField(max_length=1024)   # Название,
    nested_unit_id = models.ForeignKey('Unit', on_delete=models.DO_NOTHING, related_name='nestedUnit')  # Идентификатор вложенной единицы измерени
    parent_item_id = models.PositiveIntegerField()   # Идентификатор    группы    товаров,
    price = models.FloatField()   # Цена    товара    в    руб.,
    sid = models.PositiveIntegerField()  # Артикул,
    slug = models.CharField(max_length=1024)   # Название    товара    на    транслите    для    URL,
    supply_period = models.PositiveSmallIntegerField()  # Срок    перемещения  , дней,
    trademark_id = models.ForeignKey('Trademark', on_delete=models.DO_NOTHING)  # Идентификатор    торговой    марки,
    unit_id = models.ForeignKey('Unit', on_delete=models.DO_NOTHING) # Идентификатор    единицы    измерения,
    weight = models.FloatField()  # Вес    в    г.,
    width = models.FloatField()  # Ширина    в    см.

    def get_abs_url(self):
        return reverse('product_view', kwargs={'product_id': self.id})

class Trademark(models.Model):
    description = models.TextField(null=True)  # Описание,
    icon = models.CharField(max_length=1024)  # URL    логотипа,
    id = models.PositiveSmallIntegerField(primary_key=True)  # Идентификатор,
    name = models.CharField(max_length=256)  # Название,
    slug = models.CharField(max_length=256)  # Название    на    транслите


class Country(models.Model):
    alpha2 = models.CharField(max_length=2)  # Двубуквенный    код,
    full_name = models.CharField(max_length=512)  # Полное    название,
    id = models.PositiveSmallIntegerField(primary_key=True)   # Идентификатор,
    name = models.CharField(max_length=512)   # Название


class ItemModifier(models.Model):
    id = models.IntegerField(primary_key=True)  # Идентификатор    связи,
    item_id = models.ForeignKey('Item', on_delete=models.DO_NOTHING)  # Идентификатор    товара,
    modifier_id= models.ForeignKey('Modifier', on_delete=models.DO_NOTHING)  # Идентификатор    модификатора,
    priority = models.PositiveSmallIntegerField()  # Приоритет,
    value = models.CharField(max_length=100)   # Значение


class Modifier(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)  # Идентификатор,
    is_picture = models.BooleanField()  # Выводится    картинкой,
    name = models.CharField(max_length=200)  # Наименование


class ItemCategory(models.Model):
    category_id = models.ForeignKey('Category', on_delete=models.DO_NOTHING)  # Идентификатор    категории,
    id = models.PositiveIntegerField(primary_key=True)  # Идентификатор,
    item_id = models.ForeignKey('Item', on_delete=models.DO_NOTHING)  # Идентификатор    товара


class CategoryManager(models.Manager):
    file_name = 'categoty_tree.dmp'
    def get_category_tree(self):
        tree = Node('root')
        level = 1
        level_not_empty = True
        parents = {}
        while level_not_empty:
            list_node_on_level = Category.objects.all().filter(level=level)
            print('>'*20+f'LEVEL {level} '+'<'*20)

            if list_node_on_level.count():
                node_dict = {}
                for row in list_node_on_level:
                    row_id = str(row.id)
                    if level == 1:
                        print(f'{row.id} --> {row.name}')
                        node_dict[row_id] = Node(row_id, parent=tree, category_name=row.name)
                    else:
                        print(f'{row.id} --> {row.name}')
                        path = row.path.split('.')
                        node_dict[row_id] = Node(row_id, parents[path[-2]], category_name=row.name)
                level += 1
                parents = node_dict.copy()
            else:
                level_not_empty = False
        # RenderTree()
        return tree

    def update_tree(self):
        tree = self.get_category_tree()
        dict_tree = DictExporter().export(tree)
        with open(os.path.join(os.getcwd(), 'stat\\'+self.file_name), mode='w') as file:
            yaml.dump(dict_tree, file)

    def load_tree(self):
        try:
            with open(os.path.join(os.getcwd(), 'stat\\' + self.file_name), mode='r') as file:
                dict_tree = yaml.load(file, Loader=yaml.BaseLoader)
                print('dict_tree loaded')
            return DictImporter().import_(data=dict_tree)
        except FileNotFoundError:
            self.update_tree()
            self.load_tree()
    def get_level(self,level):
        return Category.objects.all().filter(level=level)

    def get_children(self, node_id):
        node_object = Category.objects.get(pk=node_id)
        # print(f'get Category with id {node_id} {node_object} -> {node_object.name}')
        if node_object.level > 1:
            node_in_pass_mask = '.' + str(node_object.id) + '.'
            children = Category.objects.all().filter(level=node_object.level + 1, path__icontains=node_in_pass_mask)
        else:
            node_in_pass_mask = str(node_object.id) + '.'
            children = Category.objects.all().filter(level=node_object.level + 1, path__istartswith=node_in_pass_mask)
        # print(f'children of node {node_id} is {children}')
        return children

    def get_descendants_id(self, node_id):
        node_object = Category.objects.get(pk=node_id)
        if node_object.level > 1:
            node_in_pass_mask = r'\.' + str(node_object.id) + r'\.'
            descendants = Category.objects.all().filter(level__gte=node_object.level+1,
                                                        path__regex=node_in_pass_mask).values_list('id', flat=True)
        else:
            node_in_pass_mask = str(node_object.id) + '.'
            descendants = Category.objects.all().filter(level__gt=node_object.level,
                                                        path__istartswith=node_in_pass_mask).values_list('id', flat=True)
        return descendants


class Category(models.Model):
    icon = models.URLField()  # URL - адрес    иконки,
    id = models.PositiveIntegerField(primary_key=True)  # Идентификатор,
    is_adult = models.BooleanField()  # Содержит    товары    18 +,
    is_leaf = models.BooleanField()  # Является    листом    дерева, то    есть    не    содержит    подкатегорий,
    level = models.PositiveSmallIntegerField()  # Уровень вложенности.Корневая категория  1  уровень
    name = models.CharField(max_length=100)  # Название,
    path = models.CharField(max_length=256)
    # """Путь  представляет собой список идентификаторов родителей
    # и самой категории, разделенных точкой, например, категория
    # третьего уровня с  id = 300 будет  иметь path = 100.200.300,"""
    slug = models.SlugField(max_length=256)
    # """Транслит    полного    пути, например, для    категории
    # первого    уровня - igrushki, второго    уровня - igrushki / mashinki"""
    objects = CategoryManager()

    def get_abs_url(self):
        return reverse('category_view', kwargs={'category_slug': self.slug})

    def get_bread_crumbs(self):
        path = self.path.split('.')
        crumbs_list = []
        for crumb in path[-3:]:
            crumb = Category.objects.get(pk=int(crumb))
            crumbs_list.append(crumb)
        return crumbs_list



class Unit(models.Model):
    id = models.PositiveIntegerField(primary_key=True)  # Идентификатор,
    name = models.CharField(max_length=100)  # Название


class Attribute(models.Model):
    data_type_id = models.ForeignKey('DataType', on_delete=models.DO_NOTHING)  # Идентификатор    типа    данных,
    description = models.CharField(max_length=256)  # Описание,
    id = models.PositiveSmallIntegerField(primary_key=True)  # Идентификатор,
    name = models.CharField(max_length=512)  # Название,
    unit_id = models.ForeignKey('Unit', on_delete=models.DO_NOTHING)  # Идентификатор    единицы    измерения


class ItemAttribute(models.Model):
    attribute_id = models.ForeignKey('Attribute', on_delete=models.DO_NOTHING)  # Идентификатор    атрибута,
    boolean_value = models.BooleanField()  # Булево    значение,
    datetime_value = models.DateTimeField()  # Временное    значение,
    float_value = models.FloatField()  # Дробное    значение,
    id = models.PositiveIntegerField(primary_key=True)  # Идентификатор,
    int_value = models.PositiveIntegerField()  # Целочисленное    значение,
    item_id = models.ForeignKey('Item', on_delete=models.DO_NOTHING)  # Идентификатор    товара,
    numrange_value = models.CharField(max_length=200)  # Диапазон    значения    от    и    до,
    option_value = models.ForeignKey('Option_item', on_delete=models.DO_NOTHING)  # Идентификатор  варианта значения


class DataType(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)  # Идентификатор,
    name = models.CharField(max_length=40)


class Option_item(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=200)

