from django.db import models
from django.contrib.auth.models import User,Group


class su_additional(models.Model):
    # group, created = Group.objects.get_or_create(name='default_group')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid_for_reg = models.CharField(max_length=36)
    def __str__(self):
        return(str(self.user))
    def __repr__(self):
        return (self.user.username)



