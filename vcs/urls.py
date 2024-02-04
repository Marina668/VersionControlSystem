from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.profileView, name='profile'),

    #path('repositories/', views.RepositoryListView.as_view(), name='repositories'),
    re_path(r'^repositories\/?(?P<path>[-\w\/]+)?/', views.RepositoryListView.as_view(), name='repositories'),

    path('newrepo/', views.newRepo, name='newrepo'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[-\w\/]+)?/newdir/$', views.newDir, name='newdir'),
    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[-\w\/]+)?/newfile/$', views.newFile, name='newfile'),

    re_path(r'^(?P<slug>[\w-]+)\/?(?P<path>[-\w\/]+)?/$', views.RepoDetailView.as_view(), name='repo-detail'),




]
