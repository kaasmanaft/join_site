# Generated by Django 2.2.3 on 2019-07-26 09:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='department',
        ),
        migrations.AddField(
            model_name='employee',
            name='group',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to='auth.Group'),
        ),
    ]