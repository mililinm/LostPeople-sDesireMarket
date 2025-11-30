from django.urls import path
from . import views

app_name = 'auctions'
urlpatterns = [
    path('items/', views.item_list, name='item_list'),
    path('item/new/', views.new_item, name='new_item'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('edit/<int:item_id>/', views.edit_item, name='edit_item'),      # 編集
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),  # 削除
    path("seller/<int:seller_id>/", views.seller_page, name="seller_page"),
]
