from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


from .models import Change, Milestone
from .forms import *
import os
import shutil
from pathlib import Path


from django.http import JsonResponse

PATH = Path(__file__).resolve().parent.parent.parent


def profile_view(request):
    if request.user.is_authenticated:
        return RepositoryListView.as_view()(request)
    else:
        return redirect('login')


@login_required
def new_repo(request):
    if request.method == 'POST':
        form = NewRepoForm(request.POST)
        if form.is_valid():
            detail = form.save(commit=False)
            detail.author = request.user
            detail.save()

            repositories_path = PATH.joinpath('Repositories', detail.slug, 'Content')
            os.makedirs(repositories_path)
            os.mkdir(PATH.joinpath('Repositories', detail.slug, 'History'))

            return redirect('repo-detail', slug=detail.slug)

    else:
        form = NewRepoForm()
    return render(request, 'vcs/newrepo.html', {'form': form})


def get_path(form, path, slug):
    repo = get_object_or_404(Repository, slug=slug)
    if path == '':
        pth = form.cleaned_data['name']
    else:
        pth = path + '/' + form.cleaned_data['name']
    change = Change(repo=repo, milestone=0, item=pth, change_type='a')
    change.save()
    return pth


@login_required
def new_dir(request, slug, path=''):
    if request.method == 'POST':
        form = NewDirForm(request.POST)
        if form.is_valid():
            dir_path = PATH.joinpath('Repositories', slug, 'Content', path,
                                     form.cleaned_data['name'])
            try:
                os.mkdir(dir_path)
            except FileExistsError:
                print("Directory with the same name already exists")

            pth = get_path(form, path, slug)

            return redirect('file-or-dir-view', slug=slug, path='/' + pth)

    else:
        form = NewDirForm()
    return render(request, 'vcs/newdir.html', {'form': form})


@login_required
def new_file(request, slug, path=''):
    if request.method == 'POST':
        form = NewFileForm(request.POST)
        if form.is_valid():
            dir_path = PATH.joinpath('Repositories', slug, 'Content', path,
                                     form.cleaned_data['name'])
            try:
                with open(str(dir_path), "w") as f:
                    f.write(form.cleaned_data['content'])
            except FileExistsError:
                print("File with the same name already exists")

            pth = get_path(form, path, slug)

            return redirect('file-or-dir-view', slug=slug, path='/' + pth)

    else:
        form = NewFileForm()
    return render(request, 'vcs/newfile.html', {'form': form})


@login_required
def upload_file(request, slug, path=''):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            filename = request.FILES["file"].name
            dir_path = PATH.joinpath('Repositories', slug, 'Content', path, filename)

            with open(str(dir_path), "wb+") as destination:
                for chunk in request.FILES["file"].chunks():
                    destination.write(chunk)

            repo = get_object_or_404(Repository, slug=slug)
            if path == '':
                pth = filename
            else:
                pth = path + '/' + filename
            change = Change(repo=repo, milestone=0, item=pth, change_type='a')
            change.save()

            if path != '':
                return redirect('file-or-dir-view', slug=slug, path='/' + path + '/' + filename)
            else:
                return redirect('file-or-dir-view', slug=slug, path='/' + filename)
    else:
        form = UploadFileForm()
    return render(request, "vcs/uploadfile.html", {'form': form})


def get_global_path(path, slug):
    dir_path = PATH.joinpath('Repositories', slug, 'Content', path)
    with open(str(dir_path), "r") as f:
        file_content = f.read()
    path_parts = path.split('/')
    fname = path_parts[-1]
    return file_content, fname, dir_path, path_parts


@login_required
def read_file(request, slug, path=''):
    file_content, fname, dir_path, path_parts = get_global_path(path, slug)

    context = {
        'file_name': fname,
        'file_text': file_content,
        'breadcrumbs': breadcrumbs(slug, path)
    }

    return render(request, 'vcs/readfile.html', context=context)


def save_changes(form, path, pth, slug):
    repo = get_object_or_404(Repository, slug=slug)
    if pth == '':
        p = form.cleaned_data['name']
    else:
        p = pth[:-1] + '/' + form.cleaned_data['name']
    change1 = Change(repo=repo, milestone=0, item=path, change_type='d')
    change1.save()
    change2 = Change(repo=repo, milestone=0, item=p, change_type='a')
    change2.save()


def split_path(path):
    new_path = ''
    folders = path.split('/')
    for i in range(len(folders) - 1):
        new_path += '/' + folders[i]
    return new_path, folders


@login_required
def edit_file(request, slug, path=''):
    file_content, fname, dir_path, path_parts = get_global_path(path, slug)

    if request.method == 'POST':
        form = NewFileForm(request.POST)
        if form.is_valid():
            if fname == form.cleaned_data['name']:
                if file_content != form.cleaned_data['content']:
                    with open(str(dir_path), "w") as f:
                        f.write(form.cleaned_data['content'])

                    repo = get_object_or_404(Repository, slug=slug)
                    change = Change(repo=repo, milestone=0, item=path, change_type='m')
                    change.save()
                return redirect('file-or-dir-view', slug=slug, path='/' + path)
            else:
                os.remove(dir_path)
                pth = ''
                for i in range(len(path_parts) - 1):
                    pth += path_parts[i] + '/'
                new_path = PATH.joinpath('Repositories', slug, 'Content', pth[:-1],
                                         form.cleaned_data['name'])
                with open(str(new_path), "w") as f:
                    f.write(form.cleaned_data['content'])

                save_changes(form, path, pth, slug)

                return redirect('file-or-dir-view', slug=slug, path='/' + pth + form.cleaned_data['name'])
    else:
        form = NewFileForm(initial={'name': fname, 'content': file_content})

    return render(request, 'vcs/editfile.html', {'form': form, 'slug': slug, 'path': path, 'file_name': '/' + fname})


@login_required
def edit_dir(request, slug, path=''):
    dir_path = PATH.joinpath('Repositories', slug, 'Content', path)

    path_parts = path.split('/')
    dir_name = path_parts[-1]

    if request.method == 'POST':
        form = NewDirForm(request.POST)
        if form.is_valid():
            if dir_name == form.cleaned_data['name']:
                return redirect('file-or-dir-view', slug=slug, path='/' + path)
            else:
                pth = ''
                for i in range(len(path_parts) - 1):
                    pth += path_parts[i] + '/'
                new_path = PATH.joinpath('Repositories', slug, 'Content', pth[:-1],
                                         form.cleaned_data['name'])
                os.rename(dir_path, new_path)

                save_changes(form, path, pth, slug)

                return redirect('file-or-dir-view', slug=slug, path='/' + pth + form.cleaned_data['name'])
    else:
        form = NewDirForm(initial={'name': dir_name})

    return render(request, 'vcs/editdir.html', {'form': form, 'slug': slug, 'path': path, 'dir_name': '/' + dir_name})


@login_required
def delete(request, slug, path=''):
    dir_path = PATH.joinpath('Repositories', slug, 'Content', path)
    new_path, folders = split_path(path)

    if request.method == 'POST':
        if os.path.isfile(dir_path):
            os.remove(dir_path)
        else:
            shutil.rmtree(dir_path)

        repo = get_object_or_404(Repository, slug=slug)
        change = Change(repo=repo, milestone=0, item=path, change_type='d')
        change.save()

        return redirect('file-or-dir-view', slug=slug, path=new_path)

    context = {
        'item_name': folders[-1],
        'slug': slug,
        'path': new_path,
    }

    return render(request, 'vcs/delete_item.html', context)


@login_required
def file_or_dir_view(request, slug, path=''):
    dir_path = PATH.joinpath('Repositories', slug, 'Content', path)
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


@login_required
def new_milestone(request, slug, path=''):
    dir_path = PATH.joinpath('Repositories', slug, 'Content')
    repo = get_object_or_404(Repository, slug=slug)

    if request.method == 'POST':
        form = NewMilestoneForm(request.POST)
        if form.is_valid():
            milestone = Milestone(description=form.cleaned_data['description'], author=request.user, repo=repo)
            milestone.save()

            Change.objects.filter(milestone=0, repo=repo).update(milestone=milestone.id)

            mil_path = PATH.joinpath('Repositories', slug, 'History')
            shutil.make_archive(str(mil_path.joinpath(str(milestone.id))), 'zip', str(dir_path))

            return redirect('repo-detail', slug=slug)
    else:
        form = NewMilestoneForm()
    return render(request, 'vcs/newmilestone.html', {'form': form})


@login_required
def restore_repo(request, slug, mil_id):
    content_path = PATH.joinpath('Repositories', slug, 'Content')
    dir_path = PATH.joinpath('Repositories', slug, 'Temporary')
    milestone_path = PATH.joinpath('Repositories', slug, 'History', str(mil_id) + '.zip')
    new_mil_path = PATH.joinpath('Repositories', slug, 'History')
    os.mkdir(dir_path)
    shutil.unpack_archive(milestone_path, dir_path, "zip")

    shutil.rmtree(content_path)
    os.rename(dir_path, content_path)

    mil_description = Milestone.objects.get(id=mil_id).description
    mil_id = Milestone.objects.get(id=mil_id).id
    repo = get_object_or_404(Repository, slug=slug)
    milestone = Milestone(description="repository is restored to the " + str(mil_description), author=request.user,
                          repo=repo)
    milestone.save()

    change = Change(item=mil_id, change_type='r', milestone=milestone.id,
                    repo=repo)
    change.save()

    shutil.make_archive(str(new_mil_path.joinpath(str(milestone.id))), 'zip', str(content_path))

    return redirect('repo-detail', slug=slug)


@login_required
def clone_repo(request, slug):
    repo_path = PATH.joinpath('Repositories', slug)
    name = Repository.objects.get(slug=slug).name
    if Repository.objects.get(slug=slug).author == request.user:
        author = Repository.objects.get(slug=slug).author
    else:
        author = request.user
    new_repo = Repository.objects.create(name=name, author=author)
    new_slug = new_repo.slug
    new_path = PATH.joinpath('Repositories', new_slug)
    shutil.copytree(repo_path, new_path)
    return redirect('profile')


@login_required
def delete_repo(request, slug):
    repo_path = PATH.joinpath('Repositories', slug)
    if request.method == 'POST':
        Repository.objects.filter(slug=slug).delete()
        shutil.rmtree(repo_path)
        return redirect('profile')

    context = {
        'repo_name': Repository.objects.get(slug=slug).name,
    }

    return render(request, 'vcs/delete_repo.html', context)


@login_required
def download_repo(request, slug):
    content_path = PATH.joinpath('Repositories', slug, 'Content')
    temp_dir = PATH.joinpath('Repositories', slug, 'Temporary')
    shutil.make_archive(str(temp_dir.joinpath(slug)), 'zip', str(content_path))

    filename = str(slug) + '.zip'
    filepath = temp_dir.joinpath(str(slug) + '.zip')

    with open(filepath, 'rb') as myzip:
        response = HttpResponse(myzip.read(), content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s" % filename
    shutil.rmtree(temp_dir)
    return response


@login_required
def add_user(request, slug):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            repo = get_object_or_404(Repository, slug=slug)
            username = form.cleaned_data['username']
            user = get_object_or_404(User, username=username)
            repo.users.add(user)
            return redirect('users_list', slug=slug)

    if 'term' in request.GET:
        users = User.objects.filter(username__icontains=request.GET.get('term'))
        usernames = [user.username for user in users]
        return JsonResponse(usernames, safe=False)

    else:
        form = AddUserForm()

    return render(request, 'vcs/adduser.html', {'form': form, 'slug': slug})


@login_required
def delete_user(request, slug, username):
    if request.method == 'POST':
        repo = get_object_or_404(Repository, slug=slug)
        user = get_object_or_404(User, username=username)
        repo.users.remove(user)
        return redirect('users_list', slug=slug)

    context = {
        'user_name': username,
        'slug': slug,
    }

    return render(request, 'vcs/delete_user.html', context)


@method_decorator(login_required, name='dispatch')
class RepositoryListView(generic.ListView):
    model = Repository
    template_name = 'vcs/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["path"] = self.kwargs.get("path", '')
        context['other_repo_list'] = Repository.objects.filter(users=self.request.user)

        return context

    def get_queryset(self):
        return Repository.objects.filter(author=self.request.user)


@method_decorator(login_required, name='dispatch')
class RepoDetailView(generic.DetailView):
    model = Repository
    template_name = 'vcs/repo_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["path"] = self.kwargs.get("path", '')

        pth = Path(PATH.joinpath("Repositories", self.kwargs.get("slug"), "Content", self.kwargs.get("path", '')))

        # List of directories only
        context['dirlist'] = [x for x in os.listdir(pth) if os.path.isdir(os.path.join(pth, x))]
        # List of files only
        context['filelist'] = [x for x in os.listdir(pth) if not os.path.isdir(os.path.join(pth, x))]

        context['len_list'] = len(context['dirlist']) + len(context['filelist'])

        context['breadcrumbs'] = breadcrumbs(self.kwargs.get("slug"), context['path'])

        return context


@method_decorator(login_required, name='dispatch')
class UsersListView(generic.ListView):
    model = User
    template_name = 'vcs/users_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['repo_slug'] = self.kwargs.get("slug")
        context['repo_author'] = Repository.objects.get(slug=self.kwargs.get("slug")).author
        context['user'] = self.request.user

        return context

    def get_queryset(self):
        self.repo = get_object_or_404(Repository, slug=self.kwargs.get("slug"))
        return self.repo.users.all()


@method_decorator(login_required, name='dispatch')
class MilestonesListView(generic.ListView):
    model = Milestone
    template_name = 'vcs/milestones_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['repo_slug'] = self.kwargs.get("slug")

        return context

    def get_queryset(self):
        self.repo = get_object_or_404(Repository, slug=self.kwargs["slug"])
        return Milestone.objects.filter(repo=self.repo)


@method_decorator(login_required, name='dispatch')
class ChangesListView(generic.ListView):
    model = Change
    template_name = 'vcs/milestone_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['repo_slug'] = Milestone.objects.get(pk=self.kwargs.get("pk")).repo.slug
        context['milestone_id'] = self.kwargs.get("pk")
        context['milestone_name'] = Milestone.objects.get(pk=self.kwargs.get("pk")).description

        return context

    def get_queryset(self):
        self.milestone_id = self.kwargs["pk"]
        return Change.objects.filter(milestone=self.milestone_id)
