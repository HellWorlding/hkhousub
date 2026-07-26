from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("apartment", "member", "score", "created_at")
    list_filter = ("apartment",)
