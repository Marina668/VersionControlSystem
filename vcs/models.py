from django.db import models
import uuid
from django.urls import reverse


class User(models.Model):
    """
    Model representing a system user
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    login = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.login


class Repository(models.Model):
    """
    Model representing a repository
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    author_id = models.ForeignKey('User', on_delete=models.CASCADE)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name

    def get_absolute_url(self):
        """
        Returns the url to access a particular repository information.
        """
        return reverse('repository-detail', args=[str(self.id)])


class Milestone(models.Model):
    """
    Model representing a milestone
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    description = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    author_id = models.ForeignKey('User', on_delete=models.CASCADE)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.id


class Change(models.Model):
    """
    Model representing a change
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    repo_id = models.ForeignKey('Repository', on_delete=models.CASCADE)
    milestone_id = models.ForeignKey('Milestone', on_delete=models.CASCADE)
    item = models.CharField(max_length=255)

    CHANGES = (
        ('a', 'added'),
        ('d', 'deleted'),
        ('m', 'modified'),
    )

    change_type = models.CharField(max_length=1, choices=CHANGES)


class UserRepo(models.Model):
    """
    Model representing a communication between users and repositories (which users have rights to which repositories)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    repo_id = models.ForeignKey('Repository', on_delete=models.CASCADE)