import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=30,
        unique=True,
        help_text='En fazla 30 karakter. Yalnızca harfler, rakamlar ve @/./+/-/_ izin verilir.',
        error_messages={
            'unique': 'Bu kullanıcı adı zaten alınmış.',
        },
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        error_messages={
            'unique': 'Bu e-posta adresi zaten kullanılıyor.',
        },
    )

    def __str__(self):
        return self.username
