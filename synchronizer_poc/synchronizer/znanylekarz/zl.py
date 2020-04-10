# -*- coding: utf-8 -*-
import json
from pprint import pprint

import requests

from synchronizer.models import ZlFacility, ZlDoctor, ZlAddress, ZlBooking, ZlService, ZlAddressService
from synchronizer.models import Reservation


class Calendar:
    pass


class Znanylekarz(Calendar):


    def __init__(self):
        self.base_url = 'https://www.znanylekarz.pl/api/v3/integration'
        api_key = 'api_key_placeholder'
        self.headers = {
            'Authorization': 'Bearer {}'.format(api_key),
            'Content-Type': 'application/json'}

    def api_raw_call(self, endpoint):
        return requests.get(self.base_url + endpoint, headers=self.headers)

    def api_call(self, endpoint):
        resp = requests.get(self.base_url + endpoint, headers=self.headers)
        if 'message' in resp and resp['message'] == 'Invalid credentials.':
            raise Exception("Generate new api_key")
        result = resp.json()
        if '_items' in result:
            return result['_items']
        else:
            return result

    # def sync(self):
    #     facilities = self.api_call('/facilities')
    #     for f in facilities:
    #         facility_filter = ZlFacility.objects.filter(id=f['id'])
    #         if not facility_filter.exists():
    #             facility = ZlFacility.objects.create(id=f['id'], name=f['name'])
    #         else:
    #             facility = facility_filter[0]
    #
    #         doctors = self.api_call('/facilities/{facility_id}/doctors'.format(facility_id=facility.id))
    #         for d in doctors:
    #             doctor_filter = ZlDoctor.objects.filter(id=d['id'])
    #             if not doctor_filter.exists():
    #                 doctor = ZlDoctor.objects.create(id=d['id'], facility=facility, name=d['name'], surname=d['surname'])
    #             else:
    #                 doctor = doctor_filter[0]
    #             addresses = self.api_call('/facilities/{facility_id}/doctors/{doctor_id}/addresses'.format(facility_id=facility.id, doctor_id=doctor.id))
    #             for a in addresses:
    #                 address_filter = ZlAddress.objects.filter(id=a['id'])
    #                 if not address_filter.exists():
    #                     address = ZlAddress.objects.create(id=a['id'], doctor=doctor, name=a['name'], post_code=a['post_code'], street=a['street'])
    #                 else:
    #                     address = address_filter[0]
    #
    #                 bookings = self.api_call(
    #                     '/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address}/bookings?start=2020-02-01T10%3A00%3A00%2B02%3A00&end=2020-12-31T10%3A00%3A00%2B02%3A00'.format(
    #                         facility_id=facility.id, doctor_id=doctor.id, address=address.id))
    #                 for b in bookings:
    #                     booking_filter = ZlBooking.objects.filter(id=b['id'])
    #                     if not booking_filter.exists():
    #                         booking = ZlBooking.objects.create(address=address, **b)
    #                     else:
    #                         booking = booking_filter[0]
    #
    #
    #
    #     pass

    def sync_down_resources(self):

        facilities = self.api_call('/facilities')
        for f in facilities:
            facility_filter = ZlFacility.objects.filter(id=f['id'])
            if not facility_filter.exists():
                facility = ZlFacility.objects.create(id=f['id'], name=f['name'])
            else:
                facility = facility_filter[0]

            doctors = self.api_call('/facilities/{facility_id}/doctors'.format(facility_id=facility.id))
            for d in doctors:
                doctor_filter = ZlDoctor.objects.filter(id=d['id'])
                if not doctor_filter.exists():
                    doctor = ZlDoctor.objects.create(id=d['id'], facility=facility, name=d['name'], surname=d['surname'])
                else:
                    doctor = doctor_filter[0]
                addresses = self.api_call('/facilities/{facility_id}/doctors/{doctor_id}/addresses'.format(facility_id=facility.id, doctor_id=doctor.id))
                for a in addresses:
                    address_filter = ZlAddress.objects.filter(id=a['id'])
                    if not address_filter.exists():
                        address = ZlAddress.objects.create(id=a['id'], doctor=doctor, name=a['name'], post_code=a['post_code'], street=a['street'])
                    else:
                        address = address_filter[0]
                    print("----")
                    print("facility:", f)
                    print("doctor: ", d)
                    print("address:", a)

                    address_services = self.api_call('/facilities/{facility}/doctors/{doctor}/addresses/{address}/services'.format(facility=facility.id, doctor=doctor.id, address=address.id))
                    for a_s in address_services:
                        a_s_filter = ZlAddressService.objects.filter(id=a_s['id'])
                        if not a_s_filter.exists():
                            a_s_db = ZlAddressService.objects.create(id=a_s['id'], name=a_s['name'], service_id=a_s['service_id'], is_default=a_s['is_default'], description=a_s['description'], address=address)
                            a_s_db.save()
                        else:
                            a_s_db = a_s_filter[0]

    def sync_down(self):
        for facility in ZlFacility.objects.all():
            for doctor in ZlDoctor.objects.all():
                for address in ZlAddress.objects.all():
                    bookings = self.api_call(
                        '/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address}/bookings?start=2020-02-01T10%3A00%3A00%2B02%3A00&end=2021-12-31T10%3A00%3A00%2B02%3A00'.format(
                            facility_id=facility.id, doctor_id=doctor.id, address=address.id))
                    for b in bookings:
                        booking = self.api_call(
                            '/facilities/{facility_id}/doctors/{doctor_id}/addresses/{address}/bookings/{booking}'.format(
                                facility_id=facility.id, doctor_id=doctor.id, address=address.id, booking=b['id']))
                        booking_filter = Reservation.objects.filter(zl_resource_id=b['id'])
                        # booking_filter = ZlBooking.objects.filter(id=b['id'])
                        address_service = ZlAddressService.objects.filter(id=booking['address_service']['id'])[0]
                        reservation = Reservation.convert_zl_to_reservation(booking, address, doctor, facility, address_service)
                        if not booking_filter.exists():
                            reservation.save()
                        else:
                            r_db = booking_filter[0]
                            if reservation.status != r_db.status:
                                r_db.status = reservation.status
                                r_db.save()
                            reservation = r_db

                        print('reservation', reservation)

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
