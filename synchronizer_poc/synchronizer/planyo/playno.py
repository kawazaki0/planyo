import pytz as pytz
import requests
from pprint import pprint
import datetime

from django.utils.timezone import now

from synchronizer.models import Reservation, PlResource


class Calendar:
    pass

class Planyo(Calendar):

    def __init__(self):
        self.api_key = 'api_key_placeholder'
        self.base_url = 'https://www.planyo.com/rest/'

    def api_call(self, params, endpoint=''):
        params['api_key'] = self.api_key
        return requests.get(self.base_url + endpoint, params=params)

    def sync_down_resources(self):
        response = self.api_call({'method': 'list_resources'})
        resources = response.json()['data']['resources']  # {'145682': {'name': 'Jędrzej Marcinkowski', 'id': 145682}, '145683': {'name': 'Mariusz Platoński', 'id': 145683}, '145684': {'name': 'Grzegorz Testowy', 'id': 145684}}
        for r_id, r in resources.items():
            resources_filter = PlResource.objects.filter(id=r_id)
            if not resources_filter.exists():
                PlResource.objects.create(**r)
                print(r)

    def sync_down(self):
        timestamp_start = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.timezone('Europe/Warsaw'))
        timestamp_end = timestamp_start + datetime.timedelta(days=365)
        # request_url = 'https://www.planyo.com/rest/?start_time={start_time}&end_time={end_time}&site_id=48714&api_key={api_key}&method=list_reservations'
        response = self.api_call({'method': 'list_reservations',
                                  'start_time': timestamp_start.strftime('%s'),
                                  'end_time': timestamp_end.strftime('%s')
                                  })
        results = response.json()['data']['results']

        for r in results:
            reservation_filter = Reservation.objects.filter(pl_reservation_id=r['reservation_id'])
            reservation = Reservation.convert_pl_to_reservation(r)
            if not reservation_filter.exists():
                reservation.save()
            else:
                r_db = reservation_filter[0]
                if reservation.status != r_db.status:
                    r_db.status = reservation.status
                    r_db.save()
                reservation = r_db

            print('reservation', reservation)


    def sync_up(self):
        resps = []
        for r in Reservation.objects.filter(start_time__gte=now()):
            print(r)
        #     "https://www.planyo.com/rest/?detail_level=&page=&list_resource_types=&admin_id=&prop_res_xyz=&ppp_gps_coords_radius=&ppp_resfilter=&sort=&site_id=48714&api_key=api_key_placeholder&method=list_resources"
            self.make_reservation(r)

    def make_reservation(self, reservation):
        timestamp_start = reservation.start_time #datetime.datetime(2020, 12, 1, 17, 0, tzinfo=pytz.timezone('Europe/Warsaw'))
        timestamp_end = reservation.start_time + datetime.timedelta(minutes=60)

# '?resource_id=145682' \
# '&start_time=1614618000' \
# '&end_time=1614621600' \
# '&quantity=1' \
# '&force_status=' \
# '&rental_prop_voucher=' \
# '&custom_price=' \
# '&user_id=' \
# '&email=test2%40test.com' \
# '&first_name=Test' \
# '&last_name=Testowy' \
# '&address=' \
# '&city=' \
# '&zip=' \
# '&state=' \
# '&country=' \
# '&phone_prefix=' \
# '&phone_number=' \
# '&mobile_prefix=' \
# '&mobile_number=' \
# '&user_notes=' \
# '&admin_notes=' \
# '&refcode=' \
# '&creation_time=' \
# '&cart_id=' \
# '&assignment1=' \
# '&api_key=api_key_placeholder&method=make_reservation'
        query = {
            'resource_id': reservation.pl_resource_id, #145682,
            'start_time': timestamp_start.strftime('%s'),
            'end_time': timestamp_end.strftime('%s'),
            'quantity': 1,
            'force_status': '',
            # 'rental_prop_voucher': '',
            # 'custom_price': '',
            # 'user_id': '',
            'email': reservation.email,
            'first_name': reservation.first_name,
            'last_name': reservation.last_name,
            # 'address': '',
            # 'city': '',
            # 'zip': '',
            # 'state': '',
            # 'country': '',
            # 'phone_prefix': '',
            # 'phone_number': '',
            # 'mobile_prefix': '',
            # 'mobile_number': '',
            # 'user_notes': '',
            # 'admin_notes': '',
            # 'refcode': '',
            # 'creation_time': '',
            # 'cart_id': '',
            # 'assignment1': '',
            # b'{"response_code":3,"response_message":"\'Czy jest to pierwsza wizyta u tego specjalisty?\'  cannot be empty"}'
            'api_key': self.api_key,
            'method': 'make_reservation'}

        r = requests.get('https://www.planyo.com/rest/', params=query)

        pprint(str(r) + r.text)

        return r.json()['response_code'] == 0

