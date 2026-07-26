from django.contrib import admin

from .models import Apartment, Complex


@admin.register(Complex)
class ComplexAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "created_at")
    search_fields = ("name", "region")


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ("complex", "name", "supply_count", "area", "price")
    list_filter = ("complex",)
    search_fields = ("name",)
