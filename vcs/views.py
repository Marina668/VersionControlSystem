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

            return redirect('repo-detail', slug=detail.slug)

    else:
        form = NewRepoForm()
    return render(request, 'vcs/newrepo.html', {'form': form})


def newDir(request, slug, path=''):
    if request.method == 'POST':
        form = NewDirForm(request.POST)
        if form.is_valid():
            general_path = Path(__file__).resolve().parent.parent.parent
            content_path = Repository.objects.get(slug=slug).name
            dir_path = general_path.joinpath('Repositories', Path(content_path), 'Content', path,
                                             form.cleaned_data['name'])
            try:
                os.mkdir(dir_path)
            except FileExistsError:
                print("Directory with the same name already exists")

            return redirect('repo-detail', slug=slug, path=path + form.cleaned_data['name'])

            # return HttpResponse('slug: ' + slug + ' path: ' + curr_path + '/' + form.cleaned_data['name'])

    else:
        form = NewDirForm()
    return render(request, 'vcs/newdir.html', {'form': form})


def newFile(request, slug, path=''):
    if request.method == 'POST':
        form = NewFileForm(request.POST)
        if form.is_valid():
            general_path = Path(__file__).resolve().parent.parent.parent
            content_path = Repository.objects.get(slug=slug).name
            dir_path = general_path.joinpath('Repositories', Path(content_path), 'Content', path,
                                             form.cleaned_data['name'])
            try:
                f = open(str(dir_path), "w")
                f.write(form.cleaned_data['content'])
                f.close()
            except FileExistsError:
                print("File with the same name already exists")

            return redirect('repo-detail', slug=slug, path=path)

            # return HttpResponse('slug: ' + slug + ' path: ' + curr_path)
    else:
        form = NewFileForm()
    return render(request, 'vcs/newfile.html', {'form': form})


def readFile(request, slug, path='', fname=''):
    general_path = Path(__file__).resolve().parent.parent.parent
    content_path = Repository.objects.get(slug=slug).name
    dir_path = general_path.joinpath('Repositories', Path(content_path), 'Content', path, fname)

    f = open(str(dir_path), "r")
    file_content = f.read()
    f.close()

    context = {
        'file_name': fname,
        'file_text': file_content
    }

    return render(request, 'vcs/readfile.html', context=context)


def editFile(request, slug, path='', fname=''):
    general_path = Path(__file__).resolve().parent.parent.parent
    content_path = Repository.objects.get(slug=slug).name
    dir_path = general_path.joinpath('Repositories', Path(content_path), 'Content', path, fname)

    f = open(str(dir_path), "r")
    file_content = f.read()
    f.close()

    if request.method == 'POST':
        form = NewFileForm(request.POST)
        if form.is_valid():
            if fname == form.cleaned_data['name']:
                if file_content == form.cleaned_data['content']:
                    return redirect('readfile', slug=slug, path=path, fname=fname)
                else:
                    f = open(str(dir_path), "w")
                    f.write(form.cleaned_data['content'])
                    f.close()
            else:
                os.remove(dir_path)
                new_path = general_path.joinpath('Repositories', Path(content_path), 'Content', path,
                                                 form.cleaned_data['name'])
                f = open(str(new_path), "w")
                f.write(form.cleaned_data['content'])
                f.close()
                return redirect('readfile', slug=slug, path=path, fname=form.cleaned_data['name'])

            return redirect('readfile', slug=slug, path=path, fname=fname)

    else:
        form = NewFileForm(initial={'name': fname, 'content': file_content})

    return render(request, 'vcs/editfile.html', {'form': form})


def delete(request, slug, path='', fname=''):
    return HttpResponse('slug: ' + slug + ' path: ' + path + 'fname: ' + fname)


# def test_url(request, slug, path=''):
#     folders = path.split('/')
#     return HttpResponse('slug: ' + slug + ' path: ' + folders[0] + '/' + folders[1])


class RepositoryListView(LoginRequiredMixin, generic.ListView):
    model = Repository
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context["path"] = self.kwargs.get("path", '')
        return context

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

        general_path = Path(__file__).resolve().parent.parent.parent
        name = Repository.objects.get(slug=self.kwargs.get("slug")).name

        pth = Path(general_path.joinpath("Repositories", name, "Content", self.kwargs.get("path", '')))
        # context['list_of_dirs'] = os.walk(pth)

        # List of directories only
        context['dirlist'] = [x for x in os.listdir(pth) if os.path.isdir(os.path.join(pth, x))]
        # List of files only
        context['filelist'] = [x for x in os.listdir(pth) if not os.path.isdir(os.path.join(pth, x))]

        return context


class UsersListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = 'vcs/repo_detail.html'
