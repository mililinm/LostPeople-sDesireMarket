from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from math import ceil
from django.conf import settings

class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    starting_price = models.IntegerField(default=1)
    current_price = models.IntegerField(default=0)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(default=timezone.now)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bots = models.ManyToManyField("AuctionBot", blank=True)

    def is_ended(self):
        # 無期限アイテム
        if self.end_time is None:
            return False
        
        # 通常アイテム
        return timezone.now() >= self.end_time

    def save(self, *args, **kwargs):
        if not self.current_price:
            self.current_price = self.starting_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Bid(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    amount = models.IntegerField()
    bidder = models.CharField(max_length=100, default="Unknown")
    message = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bidder} - {self.amount}円"
    
#BOT
class AuctionBot(models.Model):
    name = models.CharField(max_length=50)
    max_bid = models.IntegerField()
    aggressiveness = models.IntegerField(default=5)  # 1〜10（強気度）
    min_delay = models.FloatField(default=1.0)
    max_delay = models.FloatField(default=5.0)

    def __str__(self):
        return self.name

