from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

from pathlib import Path

from vcs.models import Repository


class NewRepoForm(forms.ModelForm):
    name = forms.CharField(max_length=255)

    class Meta:
        model = Repository
        fields = ['name']


class NewFileForm(forms.Form):
    name = forms.CharField(max_length=255, initial='')
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": "20"}), initial='')


class NewDirForm(forms.Form):
    name = forms.CharField(max_length=255)

