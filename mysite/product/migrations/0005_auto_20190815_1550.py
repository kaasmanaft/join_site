# Generated by Django 2.2.3 on 2019-08-15 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_auto_20190815_1549'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='sid',
            field=models.PositiveIntegerField(),
        ),
    ]