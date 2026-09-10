import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, Http404
from django.db import transaction
from django.db.models import F, Sum
from django.core.paginator import Paginator
from .models import Wheel, WheelOption
from .forms import WheelCreateForm

# Çark dilimleri için dinamik modern renk paletleri
PRESET_COLORS = [
    '#6C63FF', '#FF6584', '#43C6AC', '#FFB800',
    '#3B82F6', '#EC4899', '#10B981', '#8B5CF6',
    '#F97316', '#06B6D4', '#E11D48', '#84CC16',
    '#6366F1', '#14B8A6', '#F59E0B', '#A855F7',
    '#0ea5e9', '#d946ef', '#22c55e', '#ef4444'
]

def wheel_list(request):
    """Herkese açık forumda paylaşılan çarkların akışı."""
    wheels_qs = Wheel.objects.filter(is_public=True).select_related('author').prefetch_related('options')

    # Arama
    q = request.GET.get('q', '').strip()
    if q:
        wheels_qs = wheels_qs.filter(title__icontains=q)

    # Sıralama sekmeleri: En Yeniler vs Trendler/Popüler
    tab = request.GET.get('tab', 'latest').strip()
    if tab == 'popular':
        wheels_qs = wheels_qs.order_by('-spin_count', '-created_at')
    else:
        tab = 'latest'
        wheels_qs = wheels_qs.order_by('-created_at')

    # Sayfalama (Sayfa başına 6 çark)
    paginator = Paginator(wheels_qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Sidebar istatistikleri
    total_spins = Wheel.objects.aggregate(total=Sum('spin_count'))['total'] or 0
    total_public_wheels = Wheel.objects.filter(is_public=True).count()
    top_wheels = Wheel.objects.filter(is_public=True).select_related('author').order_by('-spin_count', '-created_at')[:4]

    return render(request, 'wheels/list.html', {
        'page_obj': page_obj,
        'wheels': page_obj.object_list,
        'q': q,
        'tab': tab,
        'total_count': paginator.count,
        'total_spins': total_spins,
        'total_public_wheels': total_public_wheels,
        'top_wheels': top_wheels,
    })


def wheel_detail(request, wheel_id):
    """Çarkı görüntüleme ve çevirme sayfası. Giriş yapmış ve yapmamış herkes erişebilir."""
    wheel = get_object_or_404(
        Wheel.objects.select_related('author').prefetch_related('options'),
        id=wheel_id
    )

    # Gizli çark kontrolü: Sadece sahibi görebilir
    if not wheel.is_public:
        if not request.user.is_authenticated or request.user != wheel.author:
            raise Http404("Bu çark gizlidir veya bulunamadı.")

    options = list(wheel.options.all())
    options_data = []
    for idx, opt in enumerate(options):
        # Renk belirtilmemişse paletten otomatik ata
        color = opt.color if opt.color else PRESET_COLORS[idx % len(PRESET_COLORS)]
        options_data.append({
            'id': str(opt.id),
            'text': opt.text,
            'color': color,
        })

    is_author = request.user.is_authenticated and request.user == wheel.author

    return render(request, 'wheels/detail.html', {
        'wheel': wheel,
        'options': options,
        'options_json': json.dumps(options_data),
        'is_author': is_author,
    })


def wheel_spin_record(request, wheel_id):
    """Çark her çevrildiğinde AJAX ile spin sayısını artıran endpoint."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Yalnızca POST istekleri kabul edilir.'}, status=405)

    wheel = get_object_or_404(Wheel, id=wheel_id)

    # Gizli çarksa ve sahibi değilse engelle
    if not wheel.is_public:
        if not request.user.is_authenticated or request.user != wheel.author:
            return JsonResponse({'success': False, 'error': 'Erişim reddedildi.'}, status=403)

    Wheel.objects.filter(id=wheel.id).update(spin_count=F('spin_count') + 1)
    wheel.refresh_from_db(fields=['spin_count'])

    return JsonResponse({
        'success': True,
        'spin_count': wheel.spin_count
    })


@login_required
def wheel_create(request):
    """Yeni çark oluşturma (Sadece kayıtlı/giriş yapmış kullanıcılar)."""
    if request.method == 'POST':
        form = WheelCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                wheel = form.save(commit=False)
                wheel.author = request.user
                wheel.save()

                cleaned_choices = form.cleaned_data['cleaned_choices']
                for index, choice_text in enumerate(cleaned_choices):
                    color = PRESET_COLORS[index % len(PRESET_COLORS)]
                    WheelOption.objects.create(
                        wheel=wheel,
                        text=choice_text,
                        color=color,
                        order=index
                    )

            messages.success(request, f'"{wheel.title}" karar çarkın başarıyla oluşturuldu! Şimdi çevirebilirsin.')
            return redirect('wheels:detail', wheel_id=wheel.id)
        else:
            messages.error(request, 'Lütfen formu kontrol edin ve en az 2 seçenek ekleyin.')
    else:
        form = WheelCreateForm()

    return render(request, 'wheels/create.html', {
        'form': form,
    })


@login_required
def wheel_delete(request, wheel_id):
    """Çark silme (Sadece çarkı oluşturan kullanıcı silebilir)."""
    wheel = get_object_or_404(Wheel, id=wheel_id)
    if wheel.author != request.user:
        return HttpResponseForbidden("Bu çarkı silme yetkiniz yok.")

    if request.method == 'POST':
        title = wheel.title
        wheel.delete()
        messages.success(request, f'"{title}" çarkı başarıyla silindi.')
        return redirect('accounts:profile')

    return render(request, 'wheels/confirm_delete.html', {'wheel': wheel})
