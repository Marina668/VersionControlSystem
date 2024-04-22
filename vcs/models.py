from django.db import models

from django.template.defaultfilters import slugify
from django.urls import reverse
from autoslug import AutoSlugField


class Repository(models.Model):
    """
    Model representing a repository
    """

    name = models.CharField(max_length=255)
    author = models.ForeignKey('auth.User', related_name='author', on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from=name, unique=True)
    users = models.ManyToManyField('auth.User', related_name='user')

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
    repo = models.ForeignKey('Repository', on_delete=models.CASCADE)

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
    milestone = models.IntegerField()
    item = models.CharField(max_length=255)

    CHANGES = (
        ('a', 'added'),
        ('d', 'deleted'),
        ('m', 'modified'),
        ('r', 'restored')
    )

    change_type = models.CharField(max_length=1, choices=CHANGES)
