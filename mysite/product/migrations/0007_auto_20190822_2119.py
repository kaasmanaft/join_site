# Generated by Django 2.2.3 on 2019-08-22 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_auto_20190815_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=256),
        ),
    ]
