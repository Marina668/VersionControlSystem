from django import forms

from vcs.models import Repository


class NewRepoForm(forms.Form):
    name = forms.CharField(max_length=255)

    class Meta:
        model = Repository
        fields = ['name']

    # def save(self, commit=True):
    #     repo = super(NewRepoForm, self).save(commit=False)
    #     repo.email = self.cleaned_data['email']
    #     if commit:
    #         repo.save()
    #     return repo
