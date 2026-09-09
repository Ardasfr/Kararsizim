from django import forms
from .models import Poll, Choice

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

    class Meta:
        model = Poll
        fields = ['question']

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
