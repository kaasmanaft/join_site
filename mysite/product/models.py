from django.db import models
from django.contrib.postgres.fields import ArrayField


class Item(models.Model):
    agg_photos = ArrayField(models.PositiveSmallIntegerField())  # Индексы    фотографий,
    balance = models.CharField(max_length=100, default='0')  # Баланс на    складе.
    barcodes = ArrayField(models.CharField(max_length=20))   # Штрих - коды,
    base_photo_url = models.CharField(max_length=1024)  # Базовый    url    фотографий,
    box_depth = models.FloatField()  # Глубина    упаковки    в    см.,
    box_height = models.FloatField()  # Высота    упаковки    в    см.,
    box_width = models.FloatField()  # Ширина    упаковки    в    см.,
    country_id = models.ForeignKey('Country',on_delete=models.DO_NOTHING)  # Идентификатор    страны    производителя,
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
    parent_item_id = models.PositiveSmallIntegerField()   # Идентификатор    группы    товаров,
    price= models.FloatField()   # Цена    товара    в    руб.,
    sid= models.PositiveSmallIntegerField()  # Артикул,
    slug= models.CharField(max_length=1024)   # Название    товара    на    транслите    для    URL,
    supply_period = models.PositiveSmallIntegerField()  # Срок    перемещения    в    РЦ    Екатеринбург, дней,
    trademark_id = models.ForeignKey('Trademark', on_delete=models.DO_NOTHING)  # Идентификатор    торговой    марки,
    unit_id = models.ForeignKey('Unit', on_delete=models.DO_NOTHING) # Идентификатор    единицы    измерения,
    weight = models.FloatField()  # Вес    в    г.,
    width = models.FloatField()  # Ширина    в    см.


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


class Category(models.Model):
    icon = models.URLField()  # URL - адрес    иконки,
    id = models.PositiveIntegerField(primary_key=True)  # Идентификатор,
    is_adult = models.BooleanField()  # Содержит    товары    18 +,
    is_leaf = models.BooleanField()  # Является    листом    дерева, то    есть    не    содержит    подкатегорий,
    level = models.PositiveSmallIntegerField()  # Уровень вложенности.Корневая категория принадлежит 1  уровню,
    name = models.CharField(max_length=100)  # Название,
    path = models.CharField(max_length=256)
    # """Путь  представляет собой список идентификаторов родителей
    # и самой категории, разделенных точкой, например, категория
    # третьего уровня с  id = 300 будет  иметь path = 100.200.300,"""
    slug = models.CharField(max_length=256)
    # """Транслит    полного    пути, например, для    категории
    # первого    уровня - igrushki, второго    уровня - igrushki / mashinki"""


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

