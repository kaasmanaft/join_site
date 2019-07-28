from django.db import models
from django.contrib.auth.models import User,Group


class Employee(models.Model):
    # group, created = Group.objects.get_or_create(name='default_group')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, null=True)







