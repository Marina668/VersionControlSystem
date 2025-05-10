from django.urls import path

from . import views
from .views import UserRepositoriesView, NewRepoView, NewDirView, DeleteRepo, EditDirView, CloneRepoView, NewFileView, \
    UsersView, DeleteUserView, AddUserView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('register/', views.UserRegistrationView.as_view(), name='user-register'),

    path('newrepo/', NewRepoView.as_view(), name='newrepo'),

    path('deleterepo/<int:repo_id>', DeleteRepo.as_view(), name='deleterepo'),
    path('repositories/', UserRepositoriesView.as_view(), name='user-repositories'),
    path('clonerepo/<int:repo_id>', CloneRepoView.as_view(), name='clonerepo'),

    path('newdir/', NewDirView.as_view(), name='newdir'),
    path('editdir/', EditDirView.as_view(), name='editdir'),

    path('newfile/', NewFileView.as_view(), name='newfile'),

    path('users/<int:repo_id>', UsersView.as_view(), name='users'),

    path('adduser/', AddUserView.as_view(), name='adduser'),

    path('deleteuser/<int:repo_id>/<username>', DeleteUserView.as_view(), name='deleteuser'),
]