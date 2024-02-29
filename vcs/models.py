from django.db import models
import uuid

from django.template.defaultfilters import slugify
from django.urls import reverse


class Repository(models.Model):
    """
    Model representing a repository
    """

    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    slug = models.SlugField(default="", null=False, unique=True)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name

    def get_absolute_url(self):
        """
        Returns the url to access a particular repository information.
        """
        return reverse('repository-detail', kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class Milestone(models.Model):
    """
    Model representing a milestone
    """

    description = models.TextField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.id


class Change(models.Model):
    """
    Model representing a change
    """

    repo = models.ForeignKey('Repository', on_delete=models.CASCADE)
    milestone = models.CharField(max_length=255)
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

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    repo = models.ForeignKey('Repository', on_delete=models.CASCADE)
