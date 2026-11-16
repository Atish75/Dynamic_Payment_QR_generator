from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class UPISettings(models.Model):
    upi_id = models.CharField(max_length=100)
    password = models.CharField(max_length=128)  # hashed
    banking_name = models.CharField(max_length=100, default="Mota Bhai General Store") # Apna asli bank name 
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def verify_password(self, raw_password):
        return check_password(raw_password, self.password)

    @classmethod
    def get(cls):
        return cls.objects.first()