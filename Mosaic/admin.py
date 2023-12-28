from django.contrib import admin
from django.contrib.auth.models import User, Group 
from .models import *
# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
class UserAdmin(admin.ModelAdmin):
    model = User
    # Only display the "username" field
    fields = ["username","password"]
    inlines=[ProfileInline]


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Message)
admin.site.register(Room)    
admin.site.register(Profile)