from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile'),
    path('newrepo', views.new_repo, name='newrepo'),

    path('<slug>/<int:pk>/changes', views.ChangesListView.as_view(), name='changes'),
    path('<slug>/history', views.MilestonesListView.as_view(), name='history'),
    path('<slug>/<int:mil_id>/restore', views.restore_repo, name='restore'),

    path('<slug>/users', views.UsersListView.as_view(), name='users_list'),
    path('<slug>/adduser', views.add_user, name='adduser'),
    path('<slug>/<str:username>/deleteuser', views.delete_user, name='deleteuser'),

    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/newdir$', views.new_dir, name='newdir'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/newfile$', views.new_file, name='newfile'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/uploadfile$', views.upload_file, name='uploadfile'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %.\w\/]+)?/delete$', views.delete, name='delete'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/edit$', views.edit_dir, name='editdir'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %.\w\/]+)?/edit$', views.edit_file, name='editfile'),

    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/newmilestone$', views.new_milestone, name='newmilestone'),


    re_path(r'^(?P<slug>[\w-]+)$', views.RepoDetailView.as_view(), name='repo-detail'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %.\w\/]+)$', views.file_or_dir_view, name='file-or-dir-view'),


]
