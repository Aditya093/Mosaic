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
from django.views import View
from Mosaic.forms import *
from .models import *

@not_logged_in_required
def Login(request):
    if request.method=='POST':
        username=request.POST['email']
        password=request.POST['psw']
       
        user=authenticate(request,username=username,password=password)
        
        if user is not None:
            login(request,user)
            messages.success(request,f"Welcome {username}")
            user_id=User.objects.get(username=username).id
            profile_id=Profile.objects.get(user=user_id)

            return redirect(f'profile/{profile_id.id}')
    return render(request,'Mosaic/login.html')


def Logout(request):
    logout(request)
    messages.info(request,"Logged Out")
    return redirect('login')

@login_required
def upload(request):
    if request.method=="POST":
        form=PostForm(request.POST,request.FILES)
        if form.is_valid():
            
            post=form.save(commit=False)
            post.user=request.user
            post.save()
            return redirect(f'post_list',pk=request.user.id)
    else:
        form=PostForm()        
    return render(request,'Mosaic/upload.html',{'form':form})        

@not_logged_in_required                                    
def register(request):
    if request.method=="POST":
        form=RegisterForm(request.POST,request.FILES)
        if form.is_valid():
            user=form.save(commit=False)
            phone_no=form.cleaned_data.get('phone_no')
            image=form.cleaned_data.get('image')
            user.save()
            profile,created=Profile.objects.get_or_create(user=user)
            profile.phone_no=phone_no
            profile.profile_image=image
            profile.save()
            
            return redirect('login')
            
    else:
        form=RegisterForm()
        
    return render(request,"Mosaic/register.html",{"form":form})              

@login_required
def profile_list(request):
    profiles=Profile.objects.exclude(user=request.user)
    return render(request,'Mosaic/profile_list.html',{'profiles':profiles})
@login_required
def dashboard(request):
    return render(request,'Mosaic/base.html')
@login_required
def profile(request,pk):
    if not hasattr(request.user, 'profile'):
        missing_profile = Profile(user=request.user)
        missing_profile.save()
    profile=Profile.objects.get(user_id=pk)
    posts=Post.objects.filter(user_id=request.user.id)
    
    if request.method == "POST":
        current_user_profile = request.user.profile
        data = request.POST
        action = data.get("follow")
        if action == "follow":
            current_user_profile.follows.add(profile)
        elif action == "unfollow":
            current_user_profile.follows.remove(profile)
        current_user_profile.save()
    return render(request,'Mosaic/profile.html',{'profile':profile,'posts':posts})
@login_required
def post_list(request,pk):
    if(request.user.id !=pk):
        pk=request.user.id
    profile=Profile.objects.get(user_id=pk)
    posts=Post.objects.all()
    post_comments={}
    
    if request.method=='POST':
        comment_form=CommentForm(request.POST)
        if comment_form.is_valid():
            post_id=request.POST.get('post_id')
            print(post_id)
            comment=comment_form.save(commit=False)
            comment.user=request.user
            comment.post=Post.objects.get(post_id=post_id)
            comment.save()
            return redirect('post_list', pk=profile.user.id)

    else:
        comment_form=CommentForm()        
    for post in posts:
        comments=Comment.objects.filter(post=post)
        count=len(comments)
        post_comments[post.post_id]=[comments,count]
 
    return render(request,'Mosaic/post.html',{"posts":posts,"profile":profile,"post_comments":post_comments,'comment_form':comment_form})

class GetAllUsers(View):
    @method_decorator(login_required)
    def get(self,request):

        users=Profile.objects.all()
        return render(request,'Mosaic/all_users.html',{'users':users})
    @method_decorator(login_required)
    def post(self,request):
        sender=request.user.id
        receiver=request.POST.get('users')
        print(sender,receiver)
        sender_user=User.objects.get(id=sender)
        receiver_user=User.objects.get(id=receiver)
        
        request.session['receiver_user']=receiver
        get_room= Room.objects.filter(Q(sender=sender_user,receiver=receiver_user)|
                                         Q(sender=receiver_user,receiver=sender_user))
        if get_room:
            room_name=get_room[0].room_name
        else:
            new_room=get_random_string(10)
            while True:
                room_exist=Room.objects.filter(room_name=new_room)
                if room_exist:
                    new_room=get_random_string(10)
                else:
                    break
            create_room=Room.objects.create(sender=sender_user,receiver=receiver_user,room_name=new_room)
            create_room.save()
            room_name=create_room.room_name
        return redirect('chat',room_name=room_name)
              
class ChatRoom(View):
    queryset=Room.objects.all()
    @method_decorator(login_required)
    def get(self,request,room_name,*args,**kwargs):
        get_object_or_404(Room,room_name=self.kwargs.get("room_name"))
        room=Room.objects.get(room_name=self.kwargs.get("room_name"))
        sender=request.user.id
        sender_name=Profile.objects.get(user_id=sender)
        if room.receiver.id==sender:
            receiver=room.sender.id
        else:
            
            receiver=room.receiver.id
        messages=Message.objects.filter(Q(sender=sender,receiver=receiver)|
                                       Q(sender=receiver,receiver=sender)).order_by("timestamp")
        receiver_name=Profile.objects.get(user_id=receiver)
        
        return render(request,'Mosaic/chat.html',{
            'room_name':room_name,
            'sender_id':sender,
            'receiver_id':receiver,
            'messages':messages,
            'sender_name':sender_name,
            'receiver_name':receiver_name
           
            
        })
        


@login_required
def like_post(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post = get_object_or_404(Post, post_id=post_id)
        sender=request.user.id
        receiver=request.POST.get('users')
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
                       
@login_required
def share_post(request,post_id):
    if request.method=='POST':
        
        receiver_id=request.POST.get('users')
        sender=request.user
        receiver_user=get_object_or_404(Profile,id=receiver_id).user
        
        room=Room.objects.filter(Q(sender=sender,receiver=receiver_user)|
                                         Q(sender=receiver_user,receiver=sender))
    
        if room:
            room_name=room[0].room_name
        else:
            new_room=get_random_string(10)
            while True:
                room_exist=Room.objects.filter(room_name=new_room)
                if room_exist:
                    new_room=get_random_string(10)
                else:
                    break
            create_room=Room.objects.create(sender=sender,receiver=receiver_user,room_name=new_room)
            create_room.save()
            room_name=create_room.room_name
        shared_post_link = request.build_absolute_uri(reverse('share', args=[post_id]))
      
        message_content=f"Check out the shared post: {shared_post_link}"
        Message.objects.create(sender=sender, receiver=receiver_user, content=message_content)

        messages.success(request, 'Post shared successfully!')
      
        return redirect('chat', room_name=room_name)
    post=get_object_or_404(Post,post_id=post_id)        
    users=Profile.objects.exclude(id=request.user.id)

    return render(request, 'Mosaic/shares.html', {'post': post, 'users': users})

@login_required
def shared(request,post_id):
    post=get_object_or_404(Post,post_id=post_id)
    post_comments={}
    
    if request.method=='POST':
        comment_form=CommentForm(request.POST)
        if comment_form.is_valid():
            post_id=request.POST.get('post_id')
            print(post_id)
            comment=comment_form.save(commit=False)
            comment.user=request.user
            comment.post=Post.objects.get(post_id=post_id)
            comment.save()
            return redirect('post_list', pk=profile.user.id)

    else:
        comment_form=CommentForm()        
   
    comments=Comment.objects.filter(post=post)
    count=len(comments)
    post_comments[post.post_id]=[comments,count]
    return render(request,'Mosaic/share.html',{'post':post,'post_comments':post_comments})