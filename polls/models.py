import uuid
from django.db import models
from django.conf import settings

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, verbose_name='Kategori Adı')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug')
    icon = models.CharField(max_length=10, default='💡', verbose_name='İkon / Emoji')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Sıra')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'

    def __str__(self):
        return f"{self.icon} {self.name}"


class Poll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='polls',
        verbose_name='Yazar'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='polls',
        verbose_name='Kategori'
    )
    question = models.CharField(
        max_length=300,
        verbose_name='Soru',
        help_text='Kararsız kaldığınız soruyu girin (en fazla 300 karakter).'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Sona Erme Tarihi')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Anket'
        verbose_name_plural = 'Anketler'

    def __str__(self):
        return self.question

    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False

    @property
    def time_left_display(self):
        if not self.expires_at:
            return None
        from django.utils import timezone
        if self.is_expired:
            return 'Süresi Doldu'
        diff = self.expires_at - timezone.now()
        if diff.days > 0:
            return f'{diff.days} gün kaldı'
        hours = diff.seconds // 3600
        if hours > 0:
            return f'{hours} saat kaldı'
        minutes = max(1, (diff.seconds % 3600) // 60)
        return f'{minutes} dk kaldı'

    @property
    def total_votes(self):
        return self.votes.count()

    def user_vote(self, user=None, session_key=None):
        """Kullanıcının veya anonim oturumun bu ankette kullandığı oyu döndürür."""
        if user and user.is_authenticated:
            return self.votes.filter(user=user).first()
        if session_key:
            return self.votes.filter(session_key=session_key).first()
        return None

    def has_user_voted(self, user=None, session_key=None):
        return self.user_vote(user=user, session_key=session_key) is not None


class Choice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Anket'
    )
    text = models.CharField(max_length=100, verbose_name='Seçenek Metni')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Sıra')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Seçenek'
        verbose_name_plural = 'Seçenekler'

    def __str__(self):
        return f"{self.poll.question[:30]}... -> {self.text}"

    @property
    def vote_count(self):
        return self.votes.count()

    def percentage(self):
        total = self.poll.total_votes
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100, 1)


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Anket'
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Seçilen Seçenek'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='votes',
        verbose_name='Kullanıcı'
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Oturum Anahtarı'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP Adresi'
    )
    voted_at = models.DateTimeField(auto_now_add=True, verbose_name='Oy Tarihi')

    class Meta:
        verbose_name = 'Oy'
        verbose_name_plural = 'Oylar'
        constraints = [
            # Bir kayıtlı kullanıcı bir ankette yalnızca tek bir oy verebilir
            models.UniqueConstraint(
                fields=['poll', 'user'],
                condition=models.Q(user__isnull=False),
                name='unique_user_poll_vote'
            ),
            # Bir anonim oturum bir ankette yalnızca tek bir oy verebilir
            models.UniqueConstraint(
                fields=['poll', 'session_key'],
                condition=models.Q(session_key__isnull=False),
                name='unique_session_poll_vote'
            ),
        ]

    def __str__(self):
        voter = self.user.username if self.user else f"Anonim ({self.session_key[:8]}...)"
        return f"{voter} -> {self.choice.text}"
