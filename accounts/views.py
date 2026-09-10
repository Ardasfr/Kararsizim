from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('polls:feed')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Hoş geldin, @{user.username}! Kararsız kaldığın ilk konuyu sormaya hazır mısın?')
            return redirect('polls:feed')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('polls:feed')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Tekrar hoş geldin, @{user.username}!')
            next_url = request.GET.get('next') or 'polls:feed'
            return redirect(next_url)
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    else:
        form = UserLoginForm(request)
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.method in ('POST', 'GET'):
        logout(request)
        messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('polls:feed')

@login_required
def profile_view(request):
    user_polls = request.user.polls.all().order_by('-created_at')
    total_votes_received = sum(p.total_votes for p in user_polls)
    active_polls_count = sum(1 for p in user_polls if not p.is_expired)
    expired_polls_count = sum(1 for p in user_polls if p.is_expired)

    # Karar Çarkları
    user_wheels = request.user.wheels.all().prefetch_related('options').order_by('-created_at')
    total_wheel_spins = sum(w.spin_count for w in user_wheels)

    return render(request, 'accounts/profile.html', {
        'user_polls': user_polls,
        'total_votes_received': total_votes_received,
        'active_polls_count': active_polls_count,
        'expired_polls_count': expired_polls_count,
        'user_wheels': user_wheels,
        'total_wheel_spins': total_wheel_spins,
    })
