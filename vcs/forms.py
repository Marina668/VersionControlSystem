from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

from vcs.models import Repository


class NewRepoForm(forms.ModelForm):
    name = forms.CharField(max_length=255)

    class Meta:
        model = Repository
        fields = ['name']


class NewFileForm(forms.Form):
    name = forms.CharField(max_length=255, initial='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": "20"}), initial='')


class NewDirForm(forms.Form):
    name = forms.CharField(max_length=255, initial='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))


class UploadFileForm(forms.Form):
    file = forms.FileField()


class NewMilestoneForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea(attrs={"rows": "10"}), initial='')

