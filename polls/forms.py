import datetime
from django.utils import timezone
from django import forms
from .models import Poll, Choice, Category

DURATION_CHOICES = [
    ('0', 'Süresiz (İstediğin kadar açık kalsın)'),
    ('1', '24 Saat (1 Gün)'),
    ('3', '3 Gün'),
    ('7', '1 Hafta (7 Gün)'),
]

class PollCreateForm(forms.ModelForm):
    question = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            'placeholder': 'Örn: Hangi kulaklığı almalıyım? Sony mi Apple mı?',
            'class': 'form-input question-input',
            'autocomplete': 'off',
            'required': True,
        }),
        label='Kararsız Kaldığın Konu'
    )

    duration = forms.ChoiceField(
        choices=DURATION_CHOICES,
        required=False,
        initial='0',
        widget=forms.Select(attrs={
            'class': 'form-input',
        }),
        label='Anket Süresi'
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='🏷️ Kategori Seç (İsteğe bağlı)',
        widget=forms.Select(attrs={
            'class': 'form-input',
        }),
        label='Kategori / Etiket'
    )

    class Meta:
        model = Poll
        fields = ['question', 'category']

    def calculate_expires_at(self):
        duration = self.cleaned_data.get('duration', '0')
        days = int(duration) if duration and duration.isdigit() else 0
        if days > 0:
            return timezone.now() + datetime.timedelta(days=days)
        return None

    def clean(self):
        cleaned_data = super().clean()
        post_data = self.data
        raw_choices = []

        if hasattr(post_data, 'getlist'):
            for key in post_data:
                if key == 'choices[]' or key.startswith('choice_'):
                    raw_choices.extend(post_data.getlist(key))
            if not raw_choices and 'choices' in post_data:
                raw_choices.extend(post_data.getlist('choices'))
        else:
            for key, val in post_data.items():
                if key in ('choices[]', 'choices') or key.startswith('choice_'):
                    if isinstance(val, (list, tuple)):
                        raw_choices.extend(val)
                    else:
                        raw_choices.append(val)

        choices = []
        for item in raw_choices:
            if isinstance(item, str):
                item_str = item.strip()
                if item_str and item_str not in choices:
                    choices.append(item_str)

        if len(choices) < 2:
            raise forms.ValidationError('En az 2 farklı seçenek eklemelisiniz.')
        if len(choices) > 5:
            raise forms.ValidationError('En fazla 5 seçenek ekleyebilirsiniz.')

        cleaned_data['cleaned_choices'] = choices
        return cleaned_data
