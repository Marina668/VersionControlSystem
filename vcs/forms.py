from django import forms
from dal import autocomplete
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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


class AddUserForm(forms.Form):
    username = forms.CharField(max_length=255, initial='', widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))

    # def clean(self):
    #     cleaned_data = super().clean()
    #     username = cleaned_data.get('username')
    #     if not User.objects.filter(username=username).exists():
    #         raise forms.ValidationError("The user don`t exist")
    #         # self.add_error('username', 'The user don`t exist')
    #     return username
