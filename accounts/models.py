from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        GOLDSMITH = 'goldsmith', 'Goldsmith/Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=15, blank=True)

    @property
    def is_goldsmith(self):
        return self.role == self.Role.GOLDSMITH

    def __str__(self):
        return f"{self.username} ({self.role})"
