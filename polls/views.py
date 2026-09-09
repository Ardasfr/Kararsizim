from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.core.paginator import Paginator
from .models import Poll, Choice, Vote, Category
from .forms import PollCreateForm

def get_client_ip(request):
    """Kullanıcının gerçek IP adresini tespit eder (Vercel ve proxy desteği)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def ensure_session(request):
    """Anonim kullanıcılar için geçerli bir session key bulunmasını garanti eder."""
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key

def poll_feed(request):
    """Ana sayfa: Arama, Kategori Filtresi, Trend Sekmesi ve Sayfalama ile anket akışı."""
    ensure_session(request)
    polls_qs = Poll.objects.filter(is_active=True).select_related('author', 'category').prefetch_related('choices', 'votes')

    # Arama filtresi
    q = request.GET.get('q', '').strip()
    if q:
        polls_qs = polls_qs.filter(question__icontains=q)

    # Kategori filtresi
    category_slug = request.GET.get('category', '').strip()
    current_category = None
    if category_slug:
        current_category = Category.objects.filter(slug=category_slug).first()
        if current_category:
            polls_qs = polls_qs.filter(category=current_category)

    # Sekme sıralaması: En Yeniler vs Trendler
    tab = request.GET.get('tab', 'latest').strip()
    if tab == 'trending':
        polls_qs = polls_qs.annotate(num_votes=Count('votes')).order_by('-num_votes', '-created_at')
    else:
        tab = 'latest'
        polls_qs = polls_qs.order_by('-created_at')

    # Sayfalama (Her sayfada 5 anket)
    paginator = Paginator(polls_qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    # Sidebar Sosyal Widget Verileri
    trending_widget_polls = Poll.objects.filter(is_active=True).select_related('author', 'category').prefetch_related('choices__votes', 'votes').annotate(num_votes=Count('votes')).order_by('-num_votes', '-created_at')[:4]
    total_platform_votes = Vote.objects.count()
    total_platform_polls = Poll.objects.filter(is_active=True).count()
    top_categories = Category.objects.annotate(p_count=Count('polls')).order_by('-p_count')[:6]

    return render(request, 'polls/index.html', {
        'page_obj': page_obj,
        'polls': page_obj.object_list,
        'q': q,
        'tab': tab,
        'categories': categories,
        'current_category': current_category,
        'total_count': paginator.count,
        'trending_widget_polls': trending_widget_polls,
        'total_platform_votes': total_platform_votes,
        'total_platform_polls': total_platform_polls,
        'top_categories': top_categories,
    })

def poll_detail(request, poll_id):
    """Anket detay sayfası."""
    ensure_session(request)
    poll = get_object_or_404(
        Poll.objects.select_related('author').prefetch_related('choices__votes', 'votes'),
        id=poll_id,
        is_active=True
    )
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    user_vote = poll.user_vote(user=user, session_key=session_key)
    has_voted = (user_vote is not None) or poll.is_expired

    return render(request, 'polls/detail.html', {
        'poll': poll,
        'has_voted': has_voted,
        'user_vote': user_vote,
    })

def poll_results(request, poll_id):
    """Sonuçlar sayfası. Süresi dolmuş anketlerin sonuçları herkese açıktır."""
    ensure_session(request)
    poll = get_object_or_404(Poll.objects.prefetch_related('choices__votes', 'votes'), id=poll_id, is_active=True)
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    user_vote = poll.user_vote(user=user, session_key=session_key)
    
    # Süresi dolmamışsa ve oy verilmemişse engelle
    if not poll.is_expired and not user_vote:
        messages.warning(request, 'Sonuçları görebilmek için önce oy vermelisiniz!')
        return redirect('polls:detail', poll_id=poll.id)

    return render(request, 'polls/results.html', {
        'poll': poll,
        'user_vote': user_vote,
    })

def poll_vote(request, poll_id):
    """Oy verme işlemi (Hem standart form POST hem AJAX/Fetch destekler)."""
    if request.method != 'POST':
        return redirect('polls:detail', poll_id=poll_id)

    ensure_session(request)
    poll = get_object_or_404(Poll, id=poll_id, is_active=True)
    choice_id = request.POST.get('choice')

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('ajax') == '1'

    if not choice_id:
        error_msg = 'Lütfen bir seçenek seçin.'
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('polls:detail', poll_id=poll_id)

    choice = get_object_or_404(Choice, id=choice_id, poll=poll)

    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    ip_address = get_client_ip(request)

    # Süre kontrolü
    if poll.is_expired:
        error_msg = 'Bu anketin süresi dolmuştur, artık oy kullanılamaz.'
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg, 'is_expired': True}, status=400)
        messages.warning(request, error_msg)
        return redirect('polls:results', poll_id=poll_id)

    # Çift oy kontrolü
    if poll.has_user_voted(user=user, session_key=session_key):
        error_msg = 'Bu ankette daha önce oy kullandınız!'
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg, 'already_voted': True}, status=400)
        messages.warning(request, error_msg)
        return redirect('polls:results', poll_id=poll_id)

    try:
        with transaction.atomic():
            vote = Vote.objects.create(
                poll=poll,
                choice=choice,
                user=user,
                session_key=session_key,
                ip_address=ip_address
            )
    except IntegrityError:
        error_msg = 'Bu ankette daha önce oy kullandınız!'
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg, 'already_voted': True}, status=400)
        messages.warning(request, error_msg)
        return redirect('polls:results', poll_id=poll_id)

    if is_ajax:
        # AJAX yanıtı: güncel seçenek yüzdeleri ve oy sayıları
        total = poll.total_votes
        choices_data = []
        for c in poll.choices.all():
            cnt = c.vote_count
            pct = round((cnt / total) * 100, 1) if total > 0 else 0
            choices_data.append({
                'id': str(c.id),
                'text': c.text,
                'votes': cnt,
                'percentage': pct,
                'is_selected': (c.id == choice.id)
            })

        return JsonResponse({
            'success': True,
            'message': 'Oyunuz kaydedildi!',
            'total_votes': total,
            'choices': choices_data,
            'voted_choice_id': str(choice.id),
        })

    messages.success(request, 'Oyunuz başarıyla kaydedildi!')
    return redirect('polls:results', poll_id=poll_id)

@login_required
def poll_create(request):
    """Yeni anket oluşturma (Sadece kayıtlı kullanıcılar)."""
    if request.method == 'POST':
        form = PollCreateForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                poll = form.save(commit=False)
                poll.author = request.user
                poll.expires_at = form.calculate_expires_at()
                poll.save()

                # Seçenekleri kaydet
                cleaned_choices = form.cleaned_data['cleaned_choices']
                for index, choice_text in enumerate(cleaned_choices):
                    Choice.objects.create(
                        poll=poll,
                        text=choice_text,
                        order=index
                    )

            messages.success(request, 'Anketiniz başarıyla yayınlandı!')
            return redirect('polls:detail', poll_id=poll.id)
        else:
            messages.error(request, 'Lütfen formu eksiksiz doldurun.')
    else:
        form = PollCreateForm()

    return render(request, 'polls/create.html', {
        'form': form,
    })

@login_required
def poll_delete(request, poll_id):
    """Anket silme (Sadece anket sahibi silebilir)."""
    poll = get_object_or_404(Poll, id=poll_id)
    if poll.author != request.user:
        return HttpResponseForbidden("Bu anketi silme yetkiniz yok.")

    if request.method == 'POST':
        poll.delete()
        messages.success(request, 'Anket başarıyla silindi.')
        return redirect('accounts:profile')

    return render(request, 'polls/confirm_delete.html', {'poll': poll})
