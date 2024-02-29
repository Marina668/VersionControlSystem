from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('newrepo', views.new_repo, name='newrepo'),

    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/newdir$', views.new_dir, name='newdir'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/newfile$', views.new_file, name='newfile'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/uploadfile$', views.upload_file, name='uploadfile'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %.\w\/]+)?/delete$', views.delete, name='delete'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %.\w\/]+)?/edit$', views.edit_file, name='editfile'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/newmilestone$', views.new_milestone, name='newmilestone'),

    re_path(r'^(?P<slug>[\w-]+)$', views.RepoDetailView.as_view(), name='repo-detail'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %.\w\/]+)$', views.file_or_dir_view, name='file-or-dir-view'),

]
