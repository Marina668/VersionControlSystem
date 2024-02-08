from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.profileView, name='profile'),
    re_path(r'^repositories\/?(?P<path>[-\w\/]+)?/', views.RepositoryListView.as_view(), name='repositories'),
    path('newrepo/', views.newRepo, name='newrepo'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?\/?newdir/$', views.newDir, name='newdir'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?\/?newfile/$', views.newFile, name='newfile'),

    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %.\w\/]+)?\/?delete/$', views.delete, name='delete'),

    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/$', views.RepoDetailView.as_view(), name='repo-detail'),

    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/(?P<fname>[- %.\w\/]+)?/edit/$', views.editFile,
            name='editfile'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %\w\/]+)?/(?P<fname>[- %.\w\/]+)?/$', views.readFile, name='readfile'),
    #re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[- %.\w\/]+)?/$', views.readFile, name='readfile'),


]
