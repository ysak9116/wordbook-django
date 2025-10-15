from django import forms
from .models import Term


class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ["folder", "term", "reading", "meaning", "status"]
        widgets = {
            "meaning": forms.Textarea(attrs={"rows": 3}),
        }
