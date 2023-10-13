from django import forms


class EntryForm(forms.Form):
    title = forms.CharField(max_length=50, label=False)
    content = forms.CharField(widget=forms.Textarea, required=False, label=False)