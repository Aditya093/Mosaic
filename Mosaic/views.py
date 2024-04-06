# Import necessary modules and functions
from django.shortcuts import redirect, render,get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .decorators import not_logged_in_required
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.db.models import Q
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View
from Mosaic.forms import *
from .models import *

# Decorator for views requiring user not to be logged in
@not_logged_in_required
def Login(request):
    # Handling login form submission
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['psw']
       
        user = authenticate(request, username=username, password=password)
        
        # Authenticating user
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {username}")
            user_id = User.objects.get(username=username).id
            profile_id = Profile.objects.get(user=user_id)

            # Redirecting to user's profile page
            return redirect(f'profile/{profile_id.id}')
    # Rendering login page
    return render(request, 'Mosaic/login.html')

# Handling user logout
def Logout(request):
    logout(request)
    messages.info(request, "Logged Out")
    return redirect('login')

# View for uploading posts
@login_required
def upload(request):
    # Handling post upload form submission
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect(f'post_list', pk=request.user.id)
    else:
        form = PostForm()
    # Rendering upload form
    return render(request, 'Mosaic/upload.html', {'form': form})        

# View for user registration
@not_logged_in_required                                    
def register(request):
    # Handling registration form submission
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            phone_no = form.cleaned_data.get('phone_no')
            image = form.cleaned_data.get('image')
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone_no = phone_no
            profile.profile_image = image
            profile.save()
            # Redirecting to login page after successful registration
            return redirect('login')  
    else:
        form = RegisterForm()
    # Rendering registration form
    return render(request, "Mosaic/register.html", {"form": form})              

# View for listing profiles
@login_required
def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    p = Paginator(profiles, 10)
    page = request.GET.get('page')
    try:
        profiles = p.page(page)
    except PageNotAnInteger:
        profiles = p.page(1)
    except EmptyPage:
        profiles = p.page(p.num_pages)
    # Rendering profile list
    return render(request, 'Mosaic/profile_list.html', {'profiles': profiles})

# View for dashboard
@login_required
def dashboard(request):
    # Rendering dashboard
    return render(request, 'Mosaic/base.html')

# View for user profile
@login_required
def profile(request, pk):
    # Creating profile if not exists
    if not hasattr(request.user, 'profile'):
        missing_profile = Profile(user=request.user)
        missing_profile.save()
    profile = Profile.objects.get(user_id=pk)
    posts = Post.objects.filter(user_id=pk)
    
    # Handling follow/unfollow action
    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(profile)
        current_user_profile.save()
    # Rendering user profile
    return render(request, 'Mosaic/profile.html', {'profile': profile, 'posts': posts})

# View for post list
@login_required
def post_list(request, pk):
    # Handling post comments and rendering post list
    if(request.user.id != pk):
        pk = request.user.id
    profile = Profile.objects.get(user_id=pk)
    posts = Post.objects.all()
    post_comments = {}
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            post_id = request.POST.get('post_id')
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = Post.objects.get(post_id=post_id)
            comment.save()
            return redirect('post_list', pk=profile.user.id)
    else:
        comment_form = CommentForm()        
    for post in posts:
        comments = Comment.objects.filter(post=post)
        count = len(comments)
        post_comments[post.post_id] = [comments, count]
    return render(request, 'Mosaic/post.html', {"posts": posts, "profile": profile, "post_comments": post_comments, 'comment_form': comment_form})

# View for getting all users
class GetAllUsers(View):
    # Handling GET request
    @method_decorator(login_required)
    def get(self, request):
        users = Profile.objects.all()
        return render(request, 'Mosaic/all_users.html', {'users': users})

    # Handling POST request
    @method_decorator(login_required)
    def post(self, request):
        sender = request.user.id
        receiver = request.POST.get('users')
        print(sender, receiver)
        sender_user = User.objects.get(id=sender)
        receiver_user = User.objects.get(id=receiver)
        
        request.session['receiver_user'] = receiver
        get_room = Room.objects.filter(Q(sender=sender_user, receiver=receiver_user) |
                                        Q(sender=receiver_user, receiver=sender_user))
        if get_room:
            room_name = get_room[0].room_name
        else:
            new_room = get_random_string(10)
            while True:
                room_exist = Room.objects.filter(room_name=new_room)
                if room_exist:
                    new_room = get_random_string(10)
                else:
                    break
            create_room = Room.objects.create(sender=sender_user, receiver=receiver_user, room_name=new_room)
            create_room.save()
            room_name = create_room.room_name
        return redirect('chat', room_name=room_name)

# View for chat room
class ChatRoom(View):
    queryset = Room.objects.all()

    # Handling GET request
    @method_decorator(login_required)
    def get(self, request, room_name, *args, **kwargs):
        get_object_or_404(Room, room_name=self.kwargs.get("room_name"))
        room = Room.objects.get(room_name=self.kwargs.get("room_name"))
        sender = request.user.id
        sender_name = Profile.objects.get(user_id=sender)
        if room.receiver.id == sender:
            receiver = room.sender.id
        else:
            receiver = room.receiver.id
        messages = Message.objects.filter(Q(sender=sender, receiver=receiver) |
                                          Q(sender=receiver, receiver=sender)).order_by("timestamp")
        receiver_name = Profile.objects.get(user_id=receiver)
        
        # Rendering chat room
        return render(request, 'Mosaic/chat.html', {
            'room_name': room_name,
            'sender_id': sender,
            'receiver_id': receiver,
            'messages': messages,
            'sender_name': sender_name,
            'receiver_name': receiver_name
        })

# View for liking a post
@login_required
def like_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, post_id=post_id)
        sender = request.user.id
        receiver = request.POST.get('users')
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True

        like_count = post.likes.count()
        return JsonResponse({'likes': like_count, 'liked': liked})

    # Handle other HTTP methods as needed
    return JsonResponse({'error': 'Invalid request method'})

# View for sharing a post
@login_required
def share_post(request, post_id):
    if request.method == 'POST':
        receiver_id = request.POST.get('users')
        sender = request.user
        receiver_user = get_object_or_404(Profile, id=receiver_id).user
        
        room = Room.objects.filter(Q(sender=sender, receiver=receiver_user) |
                                   Q(sender=receiver_user, receiver=sender))
    
        if room:
            room_name = room[0].room_name
        else:
            new_room = get_random_string(10)
            while True:
                room_exist = Room.objects.filter(room_name=new_room)
                if room_exist:
                    new_room = get_random_string(10)
                else:
                    break
            create_room = Room.objects.create(sender=sender, receiver=receiver_user, room_name=new_room)
            create_room.save()
            room_name = create_room.room_name
        shared_post_link = request.build_absolute_uri(reverse('share', args=[post_id]))
      
        message_content = f"Check out the shared post: {shared_post_link}"
        Message.objects.create(sender=sender, receiver=receiver_user, content=message_content)

        messages.success(request, 'Post shared successfully!')
      
        return redirect('chat', room_name=room_name)
    post = get_object_or_404(Post, post_id=post_id)        
    users = Profile.objects.exclude(id=request.user.id)

    # Rendering share post page
    return render(request, 'Mosaic/shares.html', {'post': post, 'users': users})

# View for shared post
@login_required
def shared(request, post_id):
    post = get_object_or_404(Post, post_id=post_id)
    post_comments = {}
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            post_id = request.POST.get('post_id')
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = Post.objects.get(post_id=post_id)
            comment.save()
            return redirect('post_list', pk=profile.user.id)

    else:
        comment_form = CommentForm()        
   
    comments = Comment.objects.filter(post=post)
    count = len(comments)
    post_comments[post.post_id] = [comments, count]
    # Rendering shared post page
    return render(request, 'Mosaic/share.html', {'post': post, 'post_comments': post_comments})
