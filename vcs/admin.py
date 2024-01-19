from django.contrib import admin
from .models import Repository


# Register your models here.

class RepositoryAdmin(admin.ModelAdmin):
    list_display = ("name", "author")
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Repository, RepositoryAdmin)
