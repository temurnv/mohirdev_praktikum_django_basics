from django import forms
from .models import Contact
# from django.forms import modelForm


class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = "__all__"