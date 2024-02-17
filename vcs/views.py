from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse

from .models import Repository
from .forms import *
import os
import shutil
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent.parent


def profile_view(request):
    if request.user.is_authenticated:
        return RepositoryListView.as_view()(request)
    else:
        return redirect('login')


def new_repo(request):
    if request.method == 'POST':
        form = NewRepoForm(request.POST)
        if form.is_valid():
            repositories_path = PATH.joinpath('Repositories', form.cleaned_data['name'], 'Content')
            try:
                os.makedirs(repositories_path)
                os.mkdir(PATH.joinpath('Repositories', form.cleaned_data['name'], 'History'))
            except FileExistsError:
                print("Repository with the same name already exists")

            detail = form.save(commit=False)
            detail.author = request.user
            detail.save()

            return redirect('repo-detail', slug=detail.slug)

    else:
        form = NewRepoForm()
    return render(request, 'vcs/newrepo.html', {'form': form})


def new_dir(request, slug, path=''):
    if request.method == 'POST':
        form = NewDirForm(request.POST)
        if form.is_valid():
            content_path = Repository.objects.get(slug=slug).name
            dir_path = PATH.joinpath('Repositories', Path(content_path), 'Content', path,
                                     form.cleaned_data['name'])
            try:
                os.mkdir(dir_path)
            except FileExistsError:
                print("Directory with the same name already exists")

            if path != '':
                return redirect('file-or-dir-view', slug=slug, path='/' + path + '/' + form.cleaned_data['name'])
            else:
                return redirect('file-or-dir-view', slug=slug, path='/' + form.cleaned_data['name'])

    else:
        form = NewDirForm()
    return render(request, 'vcs/newdir.html', {'form': form})


def new_file(request, slug, path=''):
    if request.method == 'POST':
        form = NewFileForm(request.POST)
        if form.is_valid():
            content_path = Repository.objects.get(slug=slug).name
            dir_path = PATH.joinpath('Repositories', Path(content_path), 'Content', path,
                                     form.cleaned_data['name'])
            try:
                f = open(str(dir_path), "w")
                f.write(form.cleaned_data['content'])
                f.close()
            except FileExistsError:
                print("File with the same name already exists")

            if path != '':
                return redirect('file-or-dir-view', slug=slug, path='/' + path + '/' + form.cleaned_data['name'])
            else:
                return redirect('file-or-dir-view', slug=slug, path='/' + form.cleaned_data['name'])

    else:
        form = NewFileForm()
    return render(request, 'vcs/newfile.html', {'form': form})


def upload_file(request, slug, path=''):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            content_path = Repository.objects.get(slug=slug).name
            filename = request.FILES["file"].name
            dir_path = PATH.joinpath('Repositories', Path(content_path), 'Content', path, filename)

            with open(str(dir_path), "wb+") as destination:
                for chunk in request.FILES["file"].chunks():
                    destination.write(chunk)

            #return redirect('file-or-dir-view', slug=slug, path='/' + path + '/' + filename)
            if path != '':
                return redirect('file-or-dir-view', slug=slug, path='/' + path + '/' + filename)
            else:
                return redirect('file-or-dir-view', slug=slug, path='/' + filename)
    else:
        form = UploadFileForm()
    return render(request, "vcs/uploadfile.html", {"form": form})


def read_file(request, slug, path=''):
    content_path = Repository.objects.get(slug=slug).name
    dir_path = PATH.joinpath('Repositories', Path(content_path), 'Content', path)

    f = open(str(dir_path), "r")
    file_content = f.read()
    f.close()

    path_parts = path.split('/')
    fname = path_parts[-1]

    context = {
        'file_name': fname,
        'file_text': file_content,
        'breadcrumbs': breadcrumbs(slug, path)
    }

    return render(request, 'vcs/readfile.html', context=context)


def edit_file(request, slug, path=''):
    content_path = Repository.objects.get(slug=slug).name
    dir_path = PATH.joinpath('Repositories', Path(content_path), 'Content', path)

    f = open(str(dir_path), "r")
    file_content = f.read()
    f.close()

    path_parts = path.split('/')
    fname = path_parts[-1]

    if request.method == 'POST':
        form = NewFileForm(request.POST)
        if form.is_valid():
            if fname == form.cleaned_data['name']:
                if file_content == form.cleaned_data['content']:
                    return redirect('file-or-dir-view', slug=slug, path='/' + path)
                else:
                    f = open(str(dir_path), "w")
                    f.write(form.cleaned_data['content'])
                    f.close()
            else:
                os.remove(dir_path)
                pth = ''
                for i in range(len(path_parts) - 1):
                    pth += path_parts[i] + '/'
                new_path = PATH.joinpath('Repositories', Path(content_path), 'Content', pth[:-1],
                                         form.cleaned_data['name'])
                f = open(str(new_path), "w")
                f.write(form.cleaned_data['content'])
                f.close()
                return redirect('file-or-dir-view', slug=slug, path='/' + pth + form.cleaned_data['name'])

            return redirect('file-or-dir-view', slug=slug, path='/' + path)

    else:
        form = NewFileForm(initial={'name': fname, 'content': file_content})

    return render(request, 'vcs/editfile.html', {'form': form})


def delete(request, slug, path=''):
    content_path = Repository.objects.get(slug=slug).name
    dir_path = PATH.joinpath('Repositories', Path(content_path), 'Content', path)

    new_path = ''
    folders = path.split('/')
    for i in range(len(folders) - 1):
        new_path += '/' + folders[i]

    if request.method == 'POST':
        if os.path.isfile(dir_path):
            os.remove(dir_path)
        else:
            shutil.rmtree(dir_path)

        return redirect('file-or-dir-view', slug=slug, path=new_path)

    context = {
        'item_name': folders[-1],
        'slug': slug,
        'path': new_path,
    }

    return render(request, 'vcs/delete_item.html', context)


def file_or_dir_view(request, slug, path=''):
    content_path = Repository.objects.get(slug=slug).name
    dir_path = PATH.joinpath('Repositories', Path(content_path), 'Content', path)
    if os.path.isfile(dir_path):
        return read_file(request, slug=slug, path=path)

    elif os.path.isdir(dir_path):
        return RepoDetailView.as_view()(request, slug=slug, path=path)


def breadcrumbs(slug, path=''):
    path_parts = path.split('/')
    result = reverse('repo-detail', kwargs={'slug': slug})
    current_path = ['<a href="' + result + '">' + slug + '</a>']
    if path != '':
        for part in path_parts[:-1]:
            result += '/' + part
            current_path.append('<a href="' + result + '">' + part + '</a>')
        current_path.append(path_parts[-1])
    return '&nbsp;/&nbsp;'.join(current_path)


class RepositoryListView(LoginRequiredMixin, generic.ListView):
    model = Repository
    template_name = 'vcs/profile.html'

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

        name = Repository.objects.get(slug=self.kwargs.get("slug")).name

        pth = Path(PATH.joinpath("Repositories", name, "Content", self.kwargs.get("path", '')))

        # List of directories only
        context['dirlist'] = [x for x in os.listdir(pth) if os.path.isdir(os.path.join(pth, x))]
        # List of files only
        context['filelist'] = [x for x in os.listdir(pth) if not os.path.isdir(os.path.join(pth, x))]

        context['len_list'] = len(context['dirlist']) + len(context['filelist'])

        context['breadcrumbs'] = breadcrumbs(self.kwargs.get("slug"), context['path'])
            
        return context


class UsersListView(LoginRequiredMixin, generic.ListView):
    model = User
    template_name = 'vcs/repo_detail.html'
