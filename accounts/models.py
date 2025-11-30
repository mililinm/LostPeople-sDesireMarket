# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    coin_balance = models.DecimalField(max_digits=12, decimal_places=2, default=50000)  # 初期残高


# Create your models here.
