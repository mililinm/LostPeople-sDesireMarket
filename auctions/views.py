import random
import threading
import time
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib import messages
from .models import Item

from .models import Item, Bid
User = get_user_model()


# BOT キャラクター設定
BOTS = [
    {
        "name": "ShadowBroker",
        "min_inc": 40,
        "max_inc": 80,
        "chance": 0.35,
        "messages": [
            "……価値を見誤っているようだな。",
            "フッ…まだまだだ。",
            "その程度か？"
        ]
    },
    {
        "name": "WhisperCollector",
        "min_inc": 10,
        "max_inc": 30,
        "chance": 0.45,
        "messages": [
            "……こっちへおいで……欲望は、まだ足りない……",
            "まだ満たされていない……",
            "ふふ……もっと上げて……"
        ]
    },
    {
        "name": "ForgottenMerchant",
        "min_inc": 20,
        "max_inc": 60,
        "chance": 0.30,
        "messages": [
            "うむ…これは手放せんな……",
            "まだ譲れん……",
            "ほほう、やるのう……"
        ]
    },
]



# BOT の入札処理
def schedule_bot_bid(item, bot_data):

    def bot_action():
        print(f"[BOT] {bot_data['name']} start for item {item.id}")

        # 入札処理に意図的な遅延を発生させる
        delay = random.uniform(3, 8)
        print(f"[BOT] delaying {delay:.2f} sec")
        time.sleep(delay)

        # 最新データを取得
        item.refresh_from_db()

        current_price = item.current_price
        inc = random.randint(bot_data["min_inc"], bot_data["max_inc"])
        new_price = current_price + inc

        # BOTユーザー作成
        bot_user, _ = User.objects.get_or_create(
            username=f"bot_{bot_data['name']}",
            defaults={"password": "!"}
        )

        Bid.objects.create(
            item=item,
            bidder=bot_user.username,
            amount=new_price,
            message=random.choice(bot_data["messages"])
        )

        item.current_price = new_price
        item.save()

        print(f"[BOT] {bot_data['name']} BID → {new_price}")

    # Django のメイン処理を止めないためにスレッドで実行
    threading.Thread(target=bot_action).start()



# 通常ビュー
def index(request):
    items = Item.objects.filter(end_time__gt=timezone.now()).order_by('end_time')[:8]
    return render(request, 'auctions/index.html', {'items': items})


def item_list(request):
    items = Item.objects.all().order_by('end_time')
    return render(request, 'auctions/item_list.html', {'items': items})


@login_required
def new_item(request):
    if request.method == 'POST':
        item = Item.objects.create(
            name=request.POST.get('name'),
            description=request.POST.get('description', ''),
            starting_price=int(request.POST.get('starting_price') or 0),
            end_time=request.POST.get('end_time'),
            image=request.FILES.get('image'),
            seller=request.user
        )
        return redirect('auctions:item_detail', item_id=item.id)

    return render(request, 'auctions/new_item.html')



# 人間の入札 + BOT 発動
@login_required
def item_detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        bid_amount = int(request.POST.get('bid_amount'))

        with transaction.atomic():
            item = Item.objects.select_for_update().get(pk=item_id)

            # 入札可能かどうか判断
            if bid_amount > item.current_price:
                # 入札追加
                Bid.objects.create(
                    item=item,
                    bidder=request.user.username,
                    amount=bid_amount,
                    comment="(user bid)"
                )
                item.current_price = bid_amount
                item.save()
                messages.success(request, "入札成功！")

                
                # BOT を確率で出現させる
                for bot in BOTS:
                    if random.random() < bot["chance"]:
                        schedule_bot_bid(item, bot)

            else:
                messages.error(request, "現在価格より高い金額で入札してください。")

        return redirect("auctions:item_detail", item_id=item.id)

    bids = Bid.objects.filter(item=item).order_by('-created_at')
    return render(request, 'auctions/item_detail.html', {'item': item, 'bids': bids})

# 編集
@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description', '')
        item.starting_price = int(request.POST.get('starting_price') or item.starting_price)
        item.end_time = request.POST.get('end_time')
        if 'image' in request.FILES:
            item.image = request.FILES['image']
        item.save()
        return redirect('auctions:item_detail', item_id=item.id)

    return render(request, 'auctions/edit_item.html', {'item': item})


# 削除 
@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, seller=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('accounts:mypage')
    return render(request, 'auctions/delete_item.html', {'item': item})


# 出品者ページ
@login_required
def seller_page(request, seller_id):
    seller = get_object_or_404(User, id=seller_id)
    items = Item.objects.filter(seller=seller)

    context = {
        'seller': seller,
        'items': items,
    }

    return render(request, 'auctions/seller_page.html', context)