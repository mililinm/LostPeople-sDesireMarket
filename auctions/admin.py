from django.contrib import admin
from .models import Item, Bid

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name','seller','current_price','starting_price','end_time')
    search_fields = ('name','description')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('item','bidder','amount','created_at')
