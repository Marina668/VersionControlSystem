from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

from vcs.models import Repository


class NewRepoForm(forms.ModelForm):
    name = forms.CharField(max_length=255)

    class Meta:
        model = Repository
        fields = ['name']
