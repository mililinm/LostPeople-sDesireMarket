from django import forms
from .models import Item
from django.utils import timezone

class ItemForm(forms.ModelForm):
    end_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now
    )

    class Meta:
        model = Item
        fields = ['name', 'description', 'starting_price', 'end_time', 'image']
