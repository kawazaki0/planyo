from django.db import models
from django.db.models import PROTECT


class Patient(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    birth_date = models.CharField(max_length=255)
    nin = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)


class ZlFacility(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.id})"


class ZlDoctor(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    facility = models.ForeignKey(to=ZlFacility, on_delete=PROTECT)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.id})"

class ZlAddress(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    doctor = models.ForeignKey(to=ZlDoctor, on_delete=PROTECT)
    name = models.CharField(max_length=255)
    post_code = models.CharField(max_length=255, null=True)
    street = models.CharField(max_length=255, null=True)

# class ZlSlot(models.Model):
#     address = models.ForeignKey(to=ZlAddress, on_delete=PROTECT)
#     start = models.DateTimeField()

class ZlService(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

class ZlAddressService(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    address = models.ForeignKey(to=ZlAddress, on_delete=PROTECT)
    # service = models.ForeignKey(to=ZlService, on_delete=PROTECT, null=True)
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=255, null=True)
    is_price_from = models.CharField(max_length=255, null=True)
    service_id = models.CharField(max_length=255, null=True)
    is_default = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255*8, null=True)

class ZlBooking(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    address = models.ForeignKey(to=ZlAddress, on_delete=PROTECT)
    address_service = models.ForeignKey(to=ZlAddressService, on_delete=PROTECT)
    # slot = models.ForeignKey(to=ZlSlot, on_delete=PROTECT)
    status = models.CharField(max_length=255)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    duration = models.IntegerField()
    booked_by = models.CharField(max_length=255)
    canceled_by = models.CharField(max_length=255, null=True)
    booked_at = models.DateTimeField()
    canceled_at = models.CharField(max_length=255, null=True)
    comment = models.CharField(max_length=255, null=True)
    insurance = models.CharField(max_length=255, null=True)

class PlResource(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)

class PlReservation(models.Model):
    reservation_id = models.CharField(max_length=255, primary_key=True)
    resource_id = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    cart_id = models.CharField(max_length=255, null=True)
    creation_time = models.DateTimeField()
    unit_assignment = models.CharField(max_length=255, null=True)
    quantity = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user_notes = models.CharField(max_length=255, null=True)
    admin_notes = models.CharField(max_length=255, null=True)
    custom_color = models.CharField(max_length=255, null=True)
    night_reservation = models.CharField(max_length=255, null=True)
    currency = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    login = models.CharField(max_length=255, null=True)
    user_id = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True)
    mobile_number = models.CharField(max_length=255, null=True)
    mobile_country_code = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    phone_country_code = models.CharField(max_length=255, null=True)
    zip = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    ppp_rs = models.CharField(max_length=255, null=True)


class Reservation(models.Model):
    # po_id = models.CharField(max_length=100)
    # zl_id = models.CharField(max_length=100)
    # doctor = models.ForeignKey(to=Patient, on_delete=PROTECT)
    # patient = models.ForeignKey(to=ZlDoctor, on_delete=PROTECT)
    # date = models.DateTimeField()
    # duration_minutes = models.IntegerField()
    pl_reservation_id = models.CharField(max_length=255, null=True)

    pl_resource = models.ForeignKey(to=PlResource, on_delete=PROTECT)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    email = models.CharField(max_length=255, default='empty@example.com')
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    zl_resource_id = models.CharField(max_length=255, null=True)
    zl_facility = models.ForeignKey(to=ZlFacility, on_delete=PROTECT)
    zl_doctor = models.ForeignKey(to=ZlDoctor, on_delete=PROTECT)
    zl_address = models.ForeignKey(to=ZlAddress, on_delete=PROTECT)
    # zl_slot = models.ForeignKey(to=ZlSlot, on_delete=PROTECT)
    zl_address_service = models.ForeignKey(to=ZlAddressService, on_delete=PROTECT)

    @staticmethod
    def convert_zl_to_reservation(zl_booking, address, doctor, facility, address_service):
        pl_resource = PlResource.objects.filter(name=doctor.name+' '+doctor.surname)[0]
        return Reservation(
            start_time=zl_booking['start_at'],
            end_time=zl_booking['end_at'],
            email=zl_booking['patient']['email'],
            first_name=zl_booking['patient']['name'],
            last_name=zl_booking['patient']['surname'],
            phone=zl_booking['patient']['phone'],
            status=zl_booking['status'],
            zl_resource_id=zl_booking['id'],
            zl_facility=facility,
            zl_doctor=doctor,
            zl_address=address,
            zl_address_service=address_service,
            pl_resource=pl_resource,
        )

    @staticmethod
    def convert_pl_to_reservation(pl_reservation):
        doctor = ZlDoctor.objects.filter(name=pl_reservation['name'].split(' ')[0],
                                         surname=pl_reservation['name'].split(' ')[1])[0]
        facility = doctor.facility
        address = ZlAddress.objects.filter(doctor=doctor)[0]
        address_service = ZlAddressService.objects.filter(address=address)[0]
        # pl_resource = PlResource.objects.filter(name=doctor.name+' '+doctor.surname)[0]
        pl_resource = PlResource.objects.filter(id=pl_reservation['resource_id'])[0]
        return Reservation(
            pl_reservation_id=pl_reservation['reservation_id'],
            pl_resource=pl_resource,
            start_time=pl_reservation['start_time'],
            end_time=pl_reservation['end_time'],
            email=pl_reservation['email'],
            first_name=pl_reservation['first_name'],
            last_name=pl_reservation['last_name'],
            phone=pl_reservation['mobile_number'],
            status=pl_reservation['status'],
            # zl_resource_id=pl_reservation['id'],
            zl_facility=facility,
            zl_doctor=doctor,
            zl_address=address,
            zl_address_service=address_service,
        )
