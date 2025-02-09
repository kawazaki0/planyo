from django.core.management.base import BaseCommand
# from synchronizer.znanylekarz.zl import Znanylekarz
from synchronizer.planyo.update_prop import UpdateUserComment


class Command(BaseCommand):

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        # for poll_id in options['poll_ids']:
        # reservations = Reservation.objects.all()

        # zl = Znanylekarz()
        # pl = Planyo()

        user_comment = UpdateUserComment()
        # zl.sync_down()

        # date_reservation = pytz.timezone('Europe/Warsaw').localize(datetime.datetime(2021, 1, 26, 20, 0, 0))

        # zl.sync_down_resources()
        # pl.sync_down_resources()

        # zl.sync_down()
        # zl.sync_up()
        # pl.sync_down()
        # pl.sync_up()

        user_comment.execute()
        # pl.sync()
        # Reservation.objects.get()
        # zl.foo(facility_id=231266,
        #                     doctor_id=343357,
        #                     address_id=925950,
        #                     start=date_reservation.strftime('%Y-%m-%dT%H:%M:%S%z'))
        # zl.make_reservation(resource_id=969582,
        #                     facility_id=231266,
        #                     doctor_id=343357,
        #                     address_id=925950,
        #                     timestamp_start=date_reservation)
        # pl.make_reservation(145682, date_reservation)

        # self.stdout.write(self.style.SUCCESS('Reservations "%s"' % reservations))
