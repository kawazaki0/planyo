from django import forms

from planyo.models import ApiKey


class CsvForm(forms.Form):
    file = forms.CharField(label='Plik csv', widget=forms.Textarea(attrs={'placeholder': 'Wklej treść pliku csv'}))

    def __init__(self, *args, **kwargs):
        super(CsvForm, self).__init__(*args, **kwargs)
        self.fields['environment'] = forms.ChoiceField(
            label='Środowisko',
            choices=[(o.environment, o.environment) for o in ApiKey.objects.all()],
            error_messages={'required': 'Wybierz środowisko'},
        )
