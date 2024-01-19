from django.urls import path
from . import views

urlpatterns = [
    path('', views.profileView, name='profile'),
    path('repositories/', views.RepositoryListView.as_view(), name='repositories'),
    path('newrepo/', views.newRepo, name='newrepo'),
]
