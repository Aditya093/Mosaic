# Import necessary modules and functions
from django import forms
from .models import Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField

# Define a form for creating or updating a post
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        
# Define a form for user registration
class RegisterForm(UserCreationForm):
    # Additional fields for user registration form
    phone_no = PhoneNumberField()
    image = forms.ImageField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone_no', 'image'] 

# Define a form for creating or updating a post (with modified widget for content)
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['image', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }
