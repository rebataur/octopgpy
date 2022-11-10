from django import forms
from . models import App,Document,Field

class AppForm(forms.ModelForm):
    class Meta:
        model = App
        fields = ('name',)

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('name',)


class FieldForm(forms.ModelForm):
    field_file = forms.FileField(required=False)
    class Meta:
        model = Field
        fields = ('name', 'descriptive_name','type','is_calculated','calculation_func','calculation_func_args','field_file',)