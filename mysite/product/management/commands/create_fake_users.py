from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User,Group


class Command(BaseCommand):
    help = 'Create fake Users'

    def add_arguments(self, parser):
        # parser.add_argument('poll_ids', nargs='+', type=int)
        pass

    def handle(self, *args, **options):

        super_user_list = ['su'+str(index) for index in range(1, 10)]
        for su_user in super_user_list:
            users = [su_user+'_user'+str(index) for index in range(1, 30)]
            suser = User.objects.create_user(username=su_user, password='gfhjkm!@#', is_staff=True, is_active=True)
            group = Group.objects.create(name=su_user)
            group.user_set.add(suser)
            for u in users:
                user = User.objects.create_user(username=u, password='gfhjkm!@#', is_staff=False, is_active=True)
                group.user_set.add(user)
        self.stdout.write(str(User.objects.all()))

        # self.stdout.write(str(all_users))
        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()
        #
        #     self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))