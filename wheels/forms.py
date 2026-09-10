from django import forms
from .models import Wheel

class WheelCreateForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Örn: Akşam Ne Yesek? / Hafta Sonu Nereye Gidelim?',
            'class': 'form-input question-input',
            'autocomplete': 'off',
            'required': True,
        }),
        label='Çark Başlığı / Kararsız Kaldığın Konu'
    )

    description = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'İsteğe bağlı: Çarkla ilgili kısa bir açıklama veya not ekleyebilirsin...',
            'class': 'form-input',
            'rows': 2,
        }),
        label='Açıklama (İsteğe bağlı)'
    )

    is_public = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-checkbox',
            'id': 'id_is_public'
        }),
        label='Forumda / Topluluk Akışında Paylaş'
    )

    class Meta:
        model = Wheel
        fields = ['title', 'description', 'is_public']

    def clean(self):
        cleaned_data = super().clean()
        post_data = self.data
        raw_choices = []

        if hasattr(post_data, 'getlist'):
            for key in post_data:
                if key in ('choices[]', 'choices') or key.startswith('choice_') or key.startswith('options'):
                    raw_choices.extend(post_data.getlist(key))
        else:
            for key, val in post_data.items():
                if key in ('choices[]', 'choices') or key.startswith('choice_') or key.startswith('options'):
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
            raise forms.ValidationError('Çark oluşturmak için en az 2 farklı seçenek eklemelisiniz.')
        if len(choices) > 20:
            raise forms.ValidationError('Bir çarka en fazla 20 seçenek ekleyebilirsiniz.')

        cleaned_data['cleaned_choices'] = choices
        return cleaned_data
