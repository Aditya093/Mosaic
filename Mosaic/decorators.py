# decorators.py
from django.shortcuts import redirect

def not_logged_in_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile',pk=request.user.id)  # Redirect to the profile page if the user is already logged in
        return view_func(request, *args, **kwargs)
    return wrapper
