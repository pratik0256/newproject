from django.contrib import admin
from .models import CustomUser, Employee

class CustomUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CustomUser._meta.fields]

admin.site.register(CustomUser, CustomUserAdmin)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Employee._meta.fields]

admin.site.register(Employee, EmployeeAdmin)
