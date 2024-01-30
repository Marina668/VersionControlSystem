from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import generic

from .models import Repository
from .forms import NewRepoForm
import os
from pathlib import Path


def profileView(request):
    if request.user.is_authenticated:
        return redirect('repositories')
    else:
        return redirect('login')


def newRepo(request):
    if request.method == 'POST':
        form = NewRepoForm(request.POST)
        if form.is_valid():
            path = Path(__file__).resolve().parent.parent.parent
            repositories_path = path.joinpath('Repositories', form.cleaned_data['name'], 'Content')
            try:
                os.makedirs(repositories_path)
                os.mkdir(path.joinpath('Repositories', form.cleaned_data['name'], 'History'))
            except FileExistsError:
                print("Repository with the same name already exists")

            detail = form.save(commit=False)
            detail.author = request.user
            detail.save()

            return redirect('profile')

    else:
        form = NewRepoForm()
    return render(request, 'vcs/newrepo.html', {'form': form})


class RepositoryListView(LoginRequiredMixin, generic.ListView):
    model = Repository
    template_name = 'profile.html'

    def get_queryset(self):
        return Repository.objects.filter(author=self.request.user)


class RepoDetailView(generic.DetailView):
    model = Repository
    template_name = 'vcs/repo_detail.html'

