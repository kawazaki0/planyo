# -*- coding: utf-8 -*-
import copy
import datetime
import functools
import json
import pandas as pd

import logging
from pprint import pprint
from urllib.parse import urlencode

import pytz
from ratelimit import sleep_and_retry, limits
import json
import requests

import os

from synchronizer.utils import timeit

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planyo.settings.dev")

import django
django.setup()

from synchronizer.models import ZlFacility, ZlDoctor, ZlAddress, ZlAddressService
from synchronizer.models import Reservation

logger = logging.getLogger(__name__)

class Calendar:
    pass

import os
import requests


class TokenExpiredException(Exception):
    pass


class Znanylekarz(Calendar):



    def __init__(self):
        self.oauth_url = 'https://www.znanylekarz.pl/oauth/v2/token'
        self.base_url = 'https://www.znanylekarz.pl/api/v3/integration'
        # api_key = 'api_key_placeholder'
        self.user = os.getenv('ZL_USER')
        self.password = os.getenv('ZL_PASS')
        self._token = None
        self.headers = {
            # 'Authorization': 'Bearer {}'.format(api_key),
            'Content-Type': 'application/json'}

    def renew_token(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if self._token is None:
                self._token = self.generate_token()
            try:
                return func(self, *args, **kwargs)
            except TokenExpiredException:
                self._token = self.generate_token()
                return func(self, *args, **kwargs)
        return wrapper

    def generate_token(self):
        logger.info("Generating new token")
        if self.user is None or self.password is None:
            raise Exception("No user or password provided")
        response = requests.post(
            self.oauth_url,
            data={'grant_type': 'client_credentials', 'scope': 'integration'},
            auth=(self.user, self.password)
        )
        if response.status_code != 200:
            logger.error(f"Error during token generation: {response.status_code}, {response.text}")
            raise Exception("Error during token generation")
        self._token = response.json()['access_token']
        return self._token

    @renew_token
    @timeit
    @sleep_and_retry
    @limits(calls=3, period=1)
    def api_call(self, endpoint, query_params=None):
        logger.info(f"Request: {self.base_url + endpoint}")
        self.headers['Authorization'] = 'Bearer {}'.format(self._token)
        resp = requests.get(self.base_url + endpoint, headers=self.headers, params=query_params)
        logger.info(f"Response: {resp.status_code}, {resp.text}")
        result = resp.json()
        if 'message' in result and result['message'] == 'Invalid credentials.':
            logger.info("Token expired or invalid")
            raise TokenExpiredException("Generate new api_key")
        return result

    def sync_down_resources_json(self):

        data = {'facilities': []}

        facilities = self.api_call('/facilities')['_items']
        for f in facilities:
            facility_data = {
                'id': f['id'],
                'name': f['name'],
                'doctors': []
            }

            doctors = self.api_call('/facilities/{facility_id}/doctors'.format(facility_id=f['id']))['_items']
            for d in doctors:
                doctor_data = {
                    'id': d['id'],
                    'name': d['name'],
                    'surname': d['surname'],
                    'addresses': []
                }

                addresses = self.api_call(
                    '/facilities/{facility_id}/doctors/{doctor_id}'.format(
                        facility_id=f['id'],
                        doctor_id=d['id'],
                    ),
                    query_params={'with[]': ["doctor.addresses"]}
                )['addresses']['_items']
                for a in addresses:
                    address_data = {
                        'id': a['id'],
                        'name': a['name'],
                        'post_code': a['post_code'],
                        'street': a['street'],
                        'services': []
                    }

                    address_services = self.api_call(
                        '/facilities/{facility}/doctors/{doctor}/addresses/{address}/services'.format(
                            facility=f['id'], doctor=d['id'], address=a['id']))['_items']
                    for a_s in address_services:
                        service_data = {
                            'id': a_s['id'],
                            'name': a_s['name'],
                            'service_id': a_s['service_id'],
                            'is_default': a_s['is_default'],
                            'description': a_s['description']
                        }
                        address_data['services'].append(service_data)

                    doctor_data['addresses'].append(address_data)
                facility_data['doctors'].append(doctor_data)
            data['facilities'].append(facility_data)
        logger.info(pprint(data))
        return data
        # with open('data.json', 'w') as json_file:
        #     json.dump(data, json_file, indent=4)

    # def sync_down(self):
    #     for facility in ZlFacility.objects.all():
    #         for doctor in ZlDoctor.objects.all():
    #             for address in ZlAddress.objects.all():
    #                 bookings = self.api_call(
    #                     '/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address}/bookings?start=2020-02-01T10%3A00%3A00%2B02%3A00&end=2021-12-31T10%3A00%3A00%2B02%3A00'.format(
    #                         facility_id=facility.id, doctor_id=doctor.id, address=address.id))['_items']
    #                 for b in bookings:
    #                     booking = self.api_call(
    #                         '/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address}/bookings/{booking}'.format(
    #                             facility_id=facility.id, doctor_id=doctor.id, address=address.id, booking=b['id']))['_items']
    #                     booking_filter = Reservation.objects.filter(zl_resource_id=b['id'])
    #                     # booking_filter = ZlBooking.objects.filter(id=b['id'])
    #                     address_service = ZlAddressService.objects.filter(id=booking['address_service']['id'])[0]
    #                     reservation = Reservation.convert_zl_to_reservation(booking, address, doctor, facility, address_service)
    #                     if not booking_filter.exists():
    #                         reservation.save()
    #                     else:
    #                         r_db = booking_filter[0]
    #                         if reservation.status != r_db.status:
    #                             r_db.status = reservation.status
    #                             r_db.save()
    #                         reservation = r_db
    #
    #                     print('reservation', reservation)

    @staticmethod
    def format_datetime(dt):
        formatted = dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        return formatted

    def sync_down_json(self, data):
        data2 = copy.copy(data)
        for facility in data['facilities']:
            for doctor in facility['doctors']:
                for address in doctor['addresses']:
                    address['bookings'] = address.get('bookings', [])
                    bookings = self.api_call(
                        endpoint='/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address}/bookings'.format(
                            facility_id=facility['id'],
                            doctor_id=doctor['id'],
                            address=address['id'],
                        ),
                        query_params={'start': self.format_datetime(datetime.datetime.now(tz=pytz.UTC) - datetime.timedelta(days=30)),
                                      'end': self.format_datetime(datetime.datetime.now(tz=pytz.UTC) + datetime.timedelta(days=10))},
                        )['_items']
                    for b in bookings:
                        booking = self.api_call(
                            '/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address}/bookings/{booking}'.format(
                                facility_id=facility['id'], doctor_id=doctor['id'], address=address['id'], booking=b['id']))
                        booking_data = {
                            'id': booking['id'],
                            'start_at': booking['start_at'],
                            'end_at': booking['end_at'],
                            'status': booking['status'],
                            'patient': {
                                'name': booking['patient']['name'],
                                'surname': booking['patient']['surname'],
                                'email': booking['patient']['email'],
                                'phone': booking['patient']['phone'],
                                'birth_date': booking['patient']['birth_date'],
                                'nin': booking['patient']['nin'],
                                'gender': booking['patient']['gender'],
                                'is_returning': booking['patient']['is_returning'],
                            },
                            'address_service': {
                                'id': booking['address_service']['id'],
                                'name': booking['address_service']['name'],
                                'price': booking['address_service']['price'],
                                'service_id': booking['address_service']['service_id'],
                                'is_visible': booking['address_service']['is_visible'],
                                'description': booking['address_service']['description'],
                            },
                        }

                        address['bookings'].append(booking_data)
        logger.info(pprint(data2))
        return data2


    # def sync_up(self):
    #     for reservation in Reservation.objects.filter(zl_resource_id=None):
    #         self.make_reservation(facility_id=facility_id,
    #                               doctor_id=doctor_id,
    #                               address_id=address_id,
    #                               res)
# jedrzej = [item for item in doctors if item['name'] == 'Jędrzej' and item['surname'] == 'Marcinkowski'][0]
# planyo_facility = [item for item in facilities if item['name'] == 'Planyo Clinic'][0]
# jedrzej_addresses = [item for item in addresses if item['name'] == 'Planyo Clinic'][0]
# jedrzej = [item for item in doctors if item['name'] == 'Jędrzej' and item['surname'] == 'Marcinkowski'][0]
# pass


    # def make_reservation(self, facility_id, doctor_id, address_id, resource_id, timestamp_start):
    #     url = self.base_url + '/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address_id}/slots/{start}/book'
    #
    #     request_url = url.format(facility_id=facility_id, doctor_id=doctor_id,
    #                              address_id=address_id, start=timestamp_start.strftime('%Y-%m-%dT%H:%M:%S%z'))
    #
    #     print(request_url)
    #
    #     payload = {
    #         "address_service_id": resource_id,  # 969582,
    #         "is_returning": False,
    #         "patient": {
    #             "name": "Abraham",
    #             "surname": "Lincoln",
    #             "email": "example@example.com",
    #             "phone": "+48123123123",
    #             "birth_date": "1985-01-01",
    #             "nin": "894237492",
    #             "gender": "m"
    #         }
    #     }
    #     resp = requests.post(request_url, data=json.dumps(payload), headers=self.headers)
    #
    #     pprint(resp.text)
    #     return resp.json()

    # def get_services(self, **kwargs):
    #     resp = self.api_call('/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address_id}/services'.format(**kwargs))
    #     return resp

    def sync_up(self):
        resps = []
        for r in Reservation.objects.all():

            url = self.base_url + '/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address_id}/slots/{start}/book'
            request_url = url.format(facility_id=r.zl_facility_id, doctor_id=r.zl_doctor_id,
                                     address_id=r.zl_address_id, start=r.start_time.strftime('%Y-%m-%dT%H:%M:%S%z'))

            print(request_url)

            payload = {
                "address_service_id": r.zl_address_service_id,  # 969582,
                "is_returning": False,
                "patient": {
                    "name": r.first_name,
                    "surname": r.last_name,
                    "email": r.email,
                    "phone": r.phone,
                    "birth_date": "1985-01-01",
                    "nin": "894237492",
                    "gender": "m"
                }
            }
            resp = requests.post(request_url, data=json.dumps(payload), headers=self.headers)
            # if resp.
            pprint(resp.text)
            resps.append(resp.json())

        return resps

    renew_token = staticmethod(renew_token)


def flatten_json(json_obj, parent_key='', sep='_'):
    items = []
    if isinstance(json_obj, dict):
        for k, v in json_obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, (dict, list)):
                items.extend(flatten_json(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
    elif isinstance(json_obj, list):
        for i, item in enumerate(json_obj):
            items.extend(flatten_json(item, f"{parent_key}{sep}{i}", sep=sep).items())
    return dict(items)


def convert_to_dataframe(resources_booking_json):
    data = []
    for facility in resources_booking_json['facilities']:
        for doctor in facility['doctors']:
            for address in doctor['addresses']:
                for booking in address.get('bookings', []):
                    flattened_booking = flatten_json({
                        'facility': facility,
                        'doctor': doctor,
                        'address': address,
                        'booking': booking
                    })
                    data.append(flattened_booking)
    df = pd.DataFrame(data)
    return df

if __name__ == '__main__':
    zl = Znanylekarz()
    resources_json = {
        'facilities': [{'doctors': [{'addresses': [{'id': '925950',
                                             'name': 'Planyo Clinic',
                                             'post_code': None,
                                             'services': [{'description': None,
                                                           'id': '969582',
                                                           'is_default': True,
                                                           'name': 'konsultacja '
                                                                   'anestezjologiczna',
                                                           'service_id': '577'}],
                                             'street': None}],
                              'id': '343357',
                              'name': 'Jędrzej',
                              'surname': 'Marcinkowski'},
                             {'addresses': [{'id': '929398',
                                             'name': 'Planyo Clinic',
                                             'post_code': None,
                                             'services': [{'description': None,
                                                           'id': '989704',
                                                           'is_default': False,
                                                           'name': 'Szczepienie',
                                                           'service_id': '1405'}],
                                             'street': None}],
                              'id': '344586',
                              'name': 'Mariusz',
                              'surname': 'Platoński'},
                             {'addresses': [{'id': '929397',
                                             'name': 'Planyo Clinic',
                                             'post_code': None,
                                             'services': [{'description': None,
                                                           'id': '989705',
                                                           'is_default': True,
                                                           'name': 'konsultacja '
                                                                   'gastrologiczna '
                                                                   'dzieci',
                                                           'service_id': '3438'}],
                                             'street': None}],
                              'id': '344585',
                              'name': 'Grzegorz',
                              'surname': 'Testowy'}],
                 'id': '231266',
                 'name': 'Planyo Clinic'}]}
    # resources_json = zl.sync_down_resources_json()
    resources_booking_json = {
        'facilities': [{'doctors': [{'addresses': [{'bookings': [{'address_service': {'description': None,
                                                                                       'id': '969582',
                                                                                       'is_visible': True,
                                                                                       'name': 'konsultacja '
                                                                                               'anestezjologiczna',
                                                                                       'price': None,
                                                                                       'service_id': '577'},
                                                                   'end_at': '2025-02-11T20:30:00+01:00',
                                                                   'id': '142456182',
                                                                   'patient': {'birth_date': '1990-02-12',
                                                                               'email': None,
                                                                               'gender': None,
                                                                               'is_returning': True,
                                                                               'name': 'Test',
                                                                               'nin': None,
                                                                               'phone': '+48789145689',
                                                                               'surname': 'Testowy2'},
                                                                   'start_at': '2025-02-11T20:00:00+01:00',
                                                                   'status': 'booked'}],
                                                     'id': '925950',
                                                     'name': 'Planyo Clinic',
                                                     'post_code': None,
                                                     'services': [{'description': None,
                                                                   'id': '969582',
                                                                   'is_default': True,
                                                                   'name': 'konsultacja '
                                                                           'anestezjologiczna',
                                                                   'service_id': '577'}],
                                                     'street': None}],
                                      'id': '343357',
                                      'name': 'Jędrzej',
                                      'surname': 'Marcinkowski'},
                                     {'addresses': [{'bookings': [{'address_service': {'description': None,
                                                                                       'id': '989704',
                                                                                       'is_visible': True,
                                                                                       'name': 'Szczepienie',
                                                                                       'price': None,
                                                                                       'service_id': '1405'},
                                                                   'end_at': '2025-02-10T11:30:00+01:00',
                                                                   'id': '142455830',
                                                                   'patient': {'birth_date': '1990-02-12',
                                                                               'email': None,
                                                                               'gender': None,
                                                                               'is_returning': False,
                                                                               'name': 'Test',
                                                                               'nin': None,
                                                                               'phone': '+48789145689',
                                                                               'surname': 'Testowy2'},
                                                                   'start_at': '2025-02-10T11:00:00+01:00',
                                                                   'status': 'booked'}],
                                                     'id': '929398',
                                                     'name': 'Planyo Clinic',
                                                     'post_code': None,
                                                     'services': [{'description': None,
                                                                   'id': '989704',
                                                                   'is_default': False,
                                                                   'name': 'Szczepienie',
                                                                   'service_id': '1405'}],
                                                     'street': None}],
                                      'id': '344586',
                                      'name': 'Mariusz',
                                      'surname': 'Platoński'},
                                     {'addresses': [{'bookings': [],
                                                     'id': '929397',
                                                     'name': 'Planyo Clinic',
                                                     'post_code': None,
                                                     'services': [{'description': None,
                                                                   'id': '989705',
                                                                   'is_default': True,
                                                                   'name': 'konsultacja '
                                                                           'gastrologiczna '
                                                                           'dzieci',
                                                                   'service_id': '3438'}],
                                                     'street': None}],
                                      'id': '344585',
                                      'name': 'Grzegorz',
                                      'surname': 'Testowy'}],
                         'id': '231266',
                         'name': 'Planyo Clinic'}]}
    # resources_booking_json = zl.sync_down_json(resources_json)
    df = convert_to_dataframe(resources_booking_json)
    print(resources_booking_json)
