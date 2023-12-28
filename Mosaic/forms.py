from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from phonenumber_field.formfields import PhoneNumberField
class PostForm(forms.ModelForm):
    class Meta:
        model=Post
        fields=['content','image']
        
class RegisterForm(UserCreationForm):
    phone_no=PhoneNumberField()
    image=forms.ImageField()
    class Meta:
        model = User
        fields=['username','email','password1','password2','phone_no','image'] 
               
class PostForm(forms.ModelForm):
    class Meta:
        model=Post
        fields=['image','content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }