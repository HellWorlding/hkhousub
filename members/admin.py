from django.contrib import admin

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "score", "created_at")
    search_fields = ("name",)
    ordering = ("-score",)
