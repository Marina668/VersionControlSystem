import base64
import os
import shutil
from pathlib import Path

from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, \
    UpdateAPIView, GenericAPIView
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.serializers import UserRegistrationSerializer, RepositorySerializer, DirectorySerializer, \
    RenameDirectorySerializer, FileSerializer, UsersSerializer, UserAddDeleteSerializer, RepositoryListSerializer, \
    RenameFileSerializer, MilestoneSerializer
from vcs.models import Repository, Milestone, Change

PATH = Path(__file__).resolve().parent.parent.parent


# class UserRegistrationView(APIView):
#     def post(self, request):
#         serializer = UserRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message': 'Користувач успішно зареєстрований'}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# def get_user_id_from_token(token):
#     try:
#         decoded_token = AccessToken(token)
#         return decoded_token['user_id']
#     except Exception as e:
#         return None


class NewRepoView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    model = Repository
    serializer_class = RepositorySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        repositories_path = PATH.joinpath('Repositories', response.data["slug"], 'Content')
        os.makedirs(repositories_path)
        os.mkdir(PATH.joinpath('Repositories', response.data["slug"], 'History'))

        return Response(
            {
                "message": "New repository successfully created!",
                "repo_id": response.data["id"],
            },
            status=status.HTTP_201_CREATED
        )


class DeleteRepo(APIView):
    permission_classes = [IsAuthenticated]
    model = Repository

    def delete(self, request, repo_id):
        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == repo.author:
            return Response({'detail': 'User cannot delete repository'}, status=status.HTTP_400_BAD_REQUEST)

        repo_path = PATH.joinpath('Repositories', repo.slug)

        try:
            if os.path.exists(repo_path) and os.path.isdir(repo_path):
                Repository.objects.filter(slug=repo.slug).delete()
                shutil.rmtree(repo_path)
                return Response(
                    {
                        "message": "Repository is deleted.",
                        "repo_name": repo.name,
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"message": "Repository is not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": f"Repository deletion error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CloneRepoView(APIView):
    permission_classes = [IsAuthenticated]
    model = Repository

    def post(self, request, repo_id):
        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if repo.author == request.user:
            new_author = repo.author
        else:
            new_author = request.user

        name = Repository.objects.get(slug=repo.slug).name
        new_repo = Repository.objects.create(name=name, author=new_author)

        repo_path = PATH.joinpath('Repositories', repo.slug)
        new_slug = new_repo.slug
        new_path = PATH.joinpath('Repositories', new_slug)
        try:
            shutil.copytree(repo_path, new_path)
        except FileExistsError:
            return Response({"detail": "Destination path already exists."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": "Repository successfully cloned!",
                "repo_id": new_repo.id,
            },
            status=status.HTTP_201_CREATED
        )


class DownloadRepoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, repo_id):
        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == repo.author and not repo.users.filter(id=request.user.id).exists():
            return Response({'detail': 'User does not have access to repository'}, status=status.HTTP_400_BAD_REQUEST)

        content_path = PATH.joinpath('Repositories', repo.slug, 'Content')
        temp_dir = PATH.joinpath('Repositories', repo.slug, 'Temporary')
        zip_path = shutil.make_archive(str(temp_dir.joinpath(repo.slug)), 'zip', str(content_path))

        with open(zip_path, 'rb') as f:
            archive_base64 = base64.b64encode(f.read()).decode('utf-8')

        shutil.rmtree(temp_dir)

        return Response({
            'repo_id': repo_id,
            'archive_base64': archive_base64
        }, status=status.HTTP_200_OK)


class UserRepositoriesView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        repositories = Repository.objects.filter(author=request.user)
        other_repositories = Repository.objects.filter(users=request.user)

        repos = list(repositories) + list(other_repositories)
        serializer = RepositoryListSerializer(repos, many=True, context={'author': request.user})
        return Response(serializer.data)

def add_change(repo, path):
    change = Change(repo=repo, milestone=0, item=path, change_type='a')
    change.save()

def save_changes(name, pth, repo):
    if len(pth) == 1:
        path = name
    else:
        path = '/'.join(pth[:-1]) + "/" + name
    change1 = Change(repo=repo, milestone=0, item='/'.join(pth), change_type='d')
    change1.save()
    change2 = Change(repo=repo, milestone=0, item=path, change_type='a')
    change2.save()
    return path

class NewDirView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DirectorySerializer

    def perform_create(self, serializer):
        self.validated_data = serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        try:
            repo = Repository.objects.get(id=response.data["repo_id"])
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == repo.author and not repo.users.filter(id=request.user.id).exists():
            return Response({'detail': 'User does not have access to repository'}, status=status.HTTP_400_BAD_REQUEST)

        dir_path = PATH.joinpath('Repositories', repo.slug, 'Content', response.data["path"],
                                 response.data["name"])
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            return Response({"detail": "Directory with the same name already exists"}, status=status.HTTP_404_NOT_FOUND)

        if response.data["path"] == "":
            path = response.data["name"]
        else:
            path = response.data["path"] + "/" + response.data["name"]

        add_change(repo, path)

        return Response(
            {
                "message": "New directory successfully created!",
                "dir_path": path,
            },
            status=status.HTTP_201_CREATED
        )


@extend_schema(methods=['PUT'], exclude=True)
class EditDirView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RenameDirectorySerializer

    def patch(self, request, *args, **kwargs):
        try:
            repo = Repository.objects.get(id=request.data["repo_id"])
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == repo.author and not repo.users.filter(id=request.user.id).exists():
            return Response({'detail': 'User does not have access to repository'}, status=status.HTTP_400_BAD_REQUEST)

        dir_path = PATH.joinpath('Repositories', repo.slug, 'Content', request.data["path"])
        path_parts = request.data["path"].split('/')
        dir_name = path_parts[-1]

        if dir_name == request.data["new_name"]:
            return Response(
                {
                    "message": "Directory successfully edited!",
                    "dir_path": request.data["path"],
                },
                status=status.HTTP_200_OK)
        else:
            pth = ''
            for i in range(len(path_parts) - 1):
                pth += path_parts[i] + '/'
            new_path = PATH.joinpath('Repositories', repo.slug, 'Content', pth[:-1],
                                     request.data["new_name"])
            os.rename(dir_path, new_path)

            path = save_changes(request.data["new_name"], path_parts,  repo)

            return Response(
                {
                    "message": "Directory successfully edited!",
                    "dir_path": path,
                },
                status=status.HTTP_200_OK
            )


class NewFileView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FileSerializer

    def perform_create(self, serializer):
        self.validated_data = serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        try:
            repo = Repository.objects.get(id=response.data["repo_id"])
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == repo.author and not repo.users.filter(id=request.user.id).exists():
            return Response({'detail': 'User does not have access to repository'}, status=status.HTTP_400_BAD_REQUEST)

        file_path = PATH.joinpath('Repositories', repo.slug, 'Content', response.data["path"],
                                  response.data["name"])
        try:
            with open(str(file_path), "w") as f:
                f.write(response.data["content"])
        except FileExistsError:
            print("File with the same name already exists")

        if response.data["path"] == "":
            path = response.data["name"]
        else:
            path = response.data["path"] + "/" + response.data["name"]

        add_change(repo, path)

        return Response(
            {
                "message": "New file successfully created!",
                "file_path": path,
            },
            status=status.HTTP_201_CREATED
        )


class UploadFileView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FileSerializer

    def perform_create(self, serializer):
        self.validated_data = serializer.save()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        try:
            repo = Repository.objects.get(id=response.data["repo_id"])
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == repo.author and not repo.users.filter(id=request.user.id).exists():
            return Response({'detail': 'User does not have access to repository'}, status=status.HTTP_400_BAD_REQUEST)

        file_path = PATH.joinpath('Repositories', repo.slug, 'Content', response.data["path"],
                                  response.data["name"])
        file_bytes = base64.b64decode(response.data["content"])

        try:
            with open(str(file_path), "w") as f:
                f.write(file_bytes.decode('utf-8'))
        except FileExistsError:
            print("File with the same name already exists")

        if response.data["path"] == "":
            path = response.data["name"]
        else:
            path = response.data["path"] + "/" + response.data["name"]

        add_change(repo, path)

        return Response(
            {
                "message": "File successfully uploaded!",
                "file_path": path,
            },
            status=status.HTTP_201_CREATED
        )


def get_global_path(path, slug):
    dir_path = PATH.joinpath('Repositories', slug, 'Content', path)
    with open(str(dir_path), "r") as f:
        file_content = f.read()
    path_parts = path.split('/')
    fname = path_parts[-1]
    return file_content, fname, dir_path, path_parts


@extend_schema(methods=['PUT'], exclude=True)
class EditFileView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RenameFileSerializer

    def patch(self, request, *args, **kwargs):
        try:
            repo = Repository.objects.get(id=request.data["repo_id"])
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == repo.author and not repo.users.filter(id=request.user.id).exists():
            return Response({'detail': 'User does not have access to repository'}, status=status.HTTP_400_BAD_REQUEST)

        file_content, fname, dir_path, path_parts = get_global_path(request.data["path"], repo.slug)

        if fname == request.data["new_name"]:
            if file_content != request.data["new_content"]:
                if os.path.exists(dir_path):
                    with open(str(dir_path), "w") as f:
                        f.write(request.data["new_content"])
                    change = Change(repo=repo, milestone=0, item=request.data['path'], change_type='m')
                    change.save()
                else:
                    return Response({"detail": "The path does not exist"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "File successfully edited!","file_path": request.data['path']},status=status.HTTP_200_OK)
        else:
            os.remove(dir_path)
            pth = ''
            for i in range(len(path_parts) - 1):
                pth += path_parts[i] + '/'
            new_path = PATH.joinpath('Repositories', repo.slug, 'Content', pth[:-1], request.data["new_name"])
            with open(str(new_path), "w") as f:
                f.write(request.data["new_content"])

            path = save_changes(request.data["new_name"], path_parts, repo)

            return Response(
                {
                    "message": "File successfully edited!",
                    "file_path": path,
                },
                status=status.HTTP_200_OK
            )


class DeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, repo_id, path):
        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user == repo.author and not repo.users.filter(id=request.user.id).exists():
            return Response({'detail': 'User does not have access to repository'}, status=status.HTTP_400_BAD_REQUEST)

        dir_path = PATH.joinpath('Repositories', repo.slug, 'Content', path)

        if not dir_path.exists():
            return Response({"detail": f"Path does not exist: {path}"}, status=status.HTTP_404_NOT_FOUND)

        if os.path.isfile(dir_path):
            os.remove(dir_path)
            change = Change(repo=repo, milestone=0, item=path, change_type='d')
            change.save()
            return Response({'detail': "File deleted from the repository."}, status=status.HTTP_200_OK)
        else:
            shutil.rmtree(dir_path)
            change = Change(repo=repo, milestone=0, item=path, change_type='d')
            change.save()
            return Response({'detail': "Directory deleted from the repository."}, status=status.HTTP_200_OK)


class UsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, repo_id):
        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user != repo.author and not repo.users.filter(id=user.id).exists():
            return Response({"detail": "You do not have access to this repository."},
                            status=status.HTTP_400_BAD_REQUEST)

        users = [repo.author] + list(repo.users.exclude(id=repo.author.id))
        serializer = UsersSerializer(users, many=True, context={'author': repo.author})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddUserView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddDeleteSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        repo_id = serializer.validated_data['repo_id']
        username = serializer.validated_data['username']

        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_to_add = User.objects.get(username=username)
        except Repository.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.user != repo.author:
            return Response({"detail": "Only the author can add users"}, status=status.HTTP_404_NOT_FOUND)
        if user_to_add == repo.author:
            return Response({'detail': 'This user is already an author of repository'},
                            status=status.HTTP_400_BAD_REQUEST)
        if repo.users.filter(id=user_to_add.id).exists():
            return Response({'detail': 'User already has access'}, status=status.HTTP_400_BAD_REQUEST)

        repo.users.add(user_to_add)
        return Response({'detail': f"User '{username}' added to the repository."}, status=status.HTTP_200_OK)


class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, repo_id, username):

        try:
            repo = Repository.objects.get(id=repo_id)
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            user_to_delete = User.objects.get(username=username)
        except Repository.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # if request.user != repo.author:
        #     return Response({"detail": "Only the author can delete users"}, status=status.HTTP_404_NOT_FOUND)
        if user_to_delete == repo.author:
            return Response({'detail': 'This user is an author of repository'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not repo.users.filter(id=user_to_delete.id).exists():
            return Response({'detail': 'User does not have access to repository'}, status=status.HTTP_400_BAD_REQUEST)

        repo.users.remove(user_to_delete)
        return Response({'detail': f"User '{username}' deleted from the repository."}, status=status.HTTP_200_OK)


class CreateMilestoneView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    model = Milestone
    serializer_class = MilestoneSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        try:
            repo = Repository.objects.get(id=response.data['repo'])
        except Repository.DoesNotExist:
            return Response({"detail": "Repository not found."}, status=status.HTTP_404_NOT_FOUND)
        dir_path = PATH.joinpath('Repositories', repo.slug, 'Content')

        if request.user != repo.author and not repo.users.filter(id=request.user.id).exists():
            return Response({"detail": "You do not have access to this repository."},
                            status=status.HTTP_400_BAD_REQUEST)

        Change.objects.filter(milestone=0, repo=repo).update(milestone=response.data['id'])

        mil_path = PATH.joinpath('Repositories', repo.slug, 'History')
        shutil.make_archive(str(mil_path.joinpath(str(response.data['id']))), 'zip', str(dir_path))

        return Response(
            {
                "message": "New milestone successfully created!",
                "milestone_id": response.data['id'],
                "description": response.data['description'],
            },
            status=status.HTTP_201_CREATED
        )
