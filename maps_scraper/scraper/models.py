from django.db import models
from django.contrib.auth.models import User

class ScrapeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100)
    filter_column = models.CharField(max_length=100, blank=True, null=True)
    filter_value = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='csv_files/', blank=True, null=True)

    def __str__(self):
        return f"{self.country} - {self.city or 'No City'} - {self.category}"