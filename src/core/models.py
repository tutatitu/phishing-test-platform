from django.db import models


class CoreSettings(models.Model):
    site_name = models.CharField(max_length=100)
    maintenance_mode = models.BooleanField(default=False)
