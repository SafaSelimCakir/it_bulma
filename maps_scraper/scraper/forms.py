from django import forms
from .utils import KEYWORD_MAPPING

CATEGORY_CHOICES = [(key, key.capitalize()) for key in KEYWORD_MAPPING.keys()]
COLUMN_CHOICES = [
    ('', 'None'),
    ('Name', 'Name'),
    ('Address', 'Address'),
    ('Phone', 'Phone'),
    ('Email', 'Email'),
    ('Website', 'Website'),
]

class ScrapeForm(forms.Form):
    country = forms.CharField(max_length=100, label="Şehir")
    city = forms.CharField(max_length=100, required=False, label="İlçe (Optional)")
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label="Kategori")
    filter_column = forms.ChoiceField(choices=COLUMN_CHOICES, required=False, label="Filtre")
    filter_value = forms.CharField(max_length=100, required=False, label="Filter Value")