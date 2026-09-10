import uuid
from django.db import models
from django.conf import settings

class Wheel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wheels',
        verbose_name='Oluşturan'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Çark Başlığı',
        help_text='Karar çarkınızın konusu (örn: Akşam Ne Yiyelim?)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Açıklama / Not',
        help_text='İsteğe bağlı ek bilgi veya kurallar'
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name='Forumda / Herkese Açık Paylaş',
        help_text='İşaretlenirse çark herkese açık akışta listelenir ve diğer kullanıcılar da çevirebilir.'
    )
    spin_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Çevrilme Sayısı'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Oluşturulma Tarihi'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Güncellenme Tarihi'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Karar Çarkı'
        verbose_name_plural = 'Karar Çarkları'

    def __str__(self):
        return self.title

    @property
    def options_count(self):
        return self.options.count()


class WheelOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wheel = models.ForeignKey(
        Wheel,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name='Çark'
    )
    text = models.CharField(
        max_length=100,
        verbose_name='Seçenek Metni'
    )
    color = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Renk Kodu (Hex veya HSL)'
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Sıra'
    )

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Çark Seçeneği'
        verbose_name_plural = 'Çark Seçenekleri'

    def __str__(self):
        return f"{self.wheel.title[:25]}... -> {self.text}"
