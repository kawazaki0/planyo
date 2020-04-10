from django.db import models


class ApiKey(models.Model):
    environment = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255)

    def __str__(self):
        return self.environment
