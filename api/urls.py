from django.urls import path

from . import views
from .views import *

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

    path('registration/', views.UserRegistrationView.as_view(), name='user-register'),

    path('newrepo/', NewRepoView.as_view(), name='newrepo'),

    path('deleterepo/<int:repo_id>', DeleteRepo.as_view(), name='deleterepo'),
    path('repositories/', UserRepositoriesView.as_view(), name='user-repositories'),
    path('clonerepo/<int:repo_id>', CloneRepoView.as_view(), name='clonerepo'),
    path('downloadrepo/<int:repo_id>', DownloadRepoView.as_view(), name='downloadrepo'),

    path('newdir/', NewDirView.as_view(), name='newdir'),
    path('editdir/', EditDirView.as_view(), name='editdir'),

    path('newfile/', NewFileView.as_view(), name='newfile'),
    path('uploadfile/', UploadFileView.as_view(), name='uploadfile'),

    path('editfile/', EditFileView.as_view(), name='editfile'),

    path('delete/<int:repo_id>/<path:path>/', DeleteView.as_view(), name='delete'),

    path('users/<int:repo_id>', UsersView.as_view(), name='users'),

    path('adduser/', AddUserView.as_view(), name='adduser'),

    path('deleteuser/<int:repo_id>/<str:username>', DeleteUserView.as_view(), name='deleteuser'),

    path('createmilestone/', CreateMilestoneView.as_view(), name='createmilestone'),

    path('history/<int:repo_id>', MilestonesView.as_view(), name='history'),

    path('changes/<int:milestone_id>', ChangesView.as_view(), name='changes'),

    path('restore/', RestoreRepoView.as_view(), name='restore'),
]