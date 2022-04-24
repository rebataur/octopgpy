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
    class Meta:
        model = Field
        fields = ('name',)