from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from auctions.models import Item
from django.utils import timezone

User = get_user_model()

def redirect_to_login(request):
    return redirect('accounts:login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        email = request.POST.get('email','').strip()
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "ユーザー名とパスワードは必須です。")
            return redirect('accounts:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "そのユーザー名は既に使われています。")
            return redirect('accounts:register')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "登録が完了しました。ログインしてください。")
        return redirect('accounts:login')

    return render(request, 'accounts/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('auctions:item_list')
        else:
            messages.error(request, "ユーザー名またはパスワードが違います。")
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def mypage_view(request):
    # 入札・出品を表示するためにDBから取得
    from auctions.models import Item, Bid
    my_bids = Bid.objects.filter(bidder=request.user.username).order_by('-created_at')[:50]
    my_listings = Item.objects.filter(seller=request.user)
    my_items = Item.objects.filter(seller=request.user).order_by('-end_time')
    return render(request, 'accounts/mypage.html', {
        'my_bids': my_bids,
        'my_listings': my_listings,
        'my_items': my_items,
    })
