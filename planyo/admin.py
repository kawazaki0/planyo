from django.contrib import admin

from planyo.models import ApiKey


@admin.register(ApiKey)
class ApiKeysAdmin(admin.ModelAdmin):
    pass
