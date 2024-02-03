from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import generic
from django.http import HttpResponse

from .models import Repository
from .forms import NewRepoForm, NewFileForm, NewDirForm
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


def newDir(request, slug):
    if request.method == 'POST':
        form = NewDirForm(request.POST)
        if form.is_valid():
            path = Path(__file__).resolve().parent.parent.parent
            # dir_path = path.joinpath('Repositories', Repository.objects.get(name=), form.cleaned_data['name'])
            # try:
            #     os.mkdir(dir_path.joinpath(form.cleaned_data['name']))
            # except FileExistsError:
            #     print("Directory with the same name already exists")

            return redirect('profile')
    else:
        form = NewDirForm()
    return render(request, 'vcs/newdir.html', {'form': form})


def newFile(request, slug):
    if request.method == 'POST':
        form = NewFileForm(request.POST)
        if form.is_valid():
            return redirect('profile')
    else:
        form = NewFileForm()
    return render(request, 'vcs/newfile.html', {'form': form})


def test_url(request, slug, path=''):
    folders = path.split('/')
    return HttpResponse('slug: ' + slug + ' path: ' + folders[0] + '/' + folders[1])


class RepositoryListView(LoginRequiredMixin, generic.ListView):
    model = Repository
    template_name = 'profile.html'

    def get_queryset(self):
        return Repository.objects.filter(author=self.request.user)


class RepoDetailView(generic.DetailView):
    model = Repository
    template_name = 'vcs/repo_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context["path"] = self.kwargs.get("path", '')

        return context


class UsersListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = 'vcs/repo_detail.html'
