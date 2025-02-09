from django.contrib import admin
from .models import ZlFacility, ZlDoctor, ZlAddress, ZlService, ZlAddressService, ZlBooking, PlResource, PlReservation, \
    Reservation


@admin.register(ZlFacility)
class ZlFacilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(ZlDoctor)
class ZlDoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'surname', 'facility')
    search_fields = ('name', 'surname')
    list_filter = ('facility',)


@admin.register(ZlAddress)
class ZlAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'name', 'post_code', 'street')
    search_fields = ('name', 'post_code', 'street')
    list_filter = ('doctor',)


@admin.register(ZlService)
class ZlServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(ZlAddressService)
class ZlAddressServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'address', 'name', 'service_id', 'price', 'is_price_from', 'is_default')
    search_fields = ('name', 'service_id')
    list_filter = ('address', 'is_default')


@admin.register(ZlBooking)
class ZlBookingAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'address', 'address_service', 'status', 'start_at', 'end_at', 'duration', 'booked_by', 'canceled_by')
    search_fields = ('status', 'booked_by', 'canceled_by')
    list_filter = ('address', 'address_service', 'status')


@admin.register(PlResource)
class PlResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(PlReservation)
class PlReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_id', 'resource_id', 'status', 'start_time', 'end_time')
    search_fields = ('reservation_id', 'resource_id', 'status')
    list_filter = ('status', 'resource_id')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
    'pl_reservation_id', 'pl_resource', 'start_time', 'end_time', 'email', 'first_name', 'last_name', 'phone', 'status',
    'zl_facility', 'zl_doctor', 'zl_address', 'zl_address_service')
    search_fields = ('pl_reservation_id', 'email', 'first_name', 'last_name', 'phone', 'status')
    list_filter = ('status', 'zl_facility', 'zl_doctor', 'zl_address', 'zl_address_service')
