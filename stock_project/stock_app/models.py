from django.db import models

class stock_info(models.Model):
    id = models.AutoField(primary_key=True)  # Auto-increment ID
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    recommended_vehicle = models.CharField(max_length=255, blank=True)
    second_best = models.CharField(max_length=255, blank=True)
    third_best = models.CharField(max_length=255, blank=True)
    fourth_best = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.username
