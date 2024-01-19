from django.shortcuts import render, redirect
from django.views import generic
from .models import Repository
from .forms import NewRepoForm


def profileView(request):
    return render(request, 'profile.html')


def newRepo(request):
    if request.method == 'POST':
        form = NewRepoForm(request.POST)
        if form.is_valid():
            # repo = form.save()  # FIXME Зберегти репозиторій
            return redirect('profile')

    else:
        form = NewRepoForm()
    return render(request, 'newrepo.html', {'form': form})


class RepositoryListView(generic.ListView):
    model = Repository


class RepoDetailView(generic.DetailView):
    model = Repository
