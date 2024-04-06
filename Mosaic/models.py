# Import necessary modules and functions
from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

# Define a receiver function to create a profile for a new user upon user creation
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Create a profile instance for the newly created user
        user_profile = Profile(user=instance, id=instance.id)
        user_profile.save()
        # Automatically make the new user follow their own profile
        user_profile.follows.add(instance.profile)
        user_profile.save()

# Define the Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_no = PhoneNumberField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='images/', blank=True, null=True)
    follows = models.ManyToManyField(
        "self",
        related_name="followed_by",
        symmetrical=False,
        blank=True
    )

    # String representation of the Profile model
    def __str__(self):
        return self.user.username

# Define the Post model
class Post(models.Model):
    user = models.ForeignKey(User, related_name="follows", on_delete=models.DO_NOTHING)
    post_id = models.AutoField(auto_created=True, serialize=True, primary_key=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    content = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, through='Like', related_name='liked_posts')

    # String representation of the Post model
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

    # Meta class for ordering posts by creation date
    class Meta:
        ordering = ['-created_at']

# Define the Comment model
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    # String representation of the Comment model
    def __str__(self):
        return f"{self.user.username} - {self.time} {self.post}"

# Define a form for adding comments
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Comment Here!',
                'rows': 4,
                'cols': 50
            })
        }

# Define the Like model
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

# Define the Message model for user messages
class Message(models.Model):
    sender = models.ForeignKey(User, related_name="send_messages", on_delete=models.CASCADE)      
    receiver = models.ForeignKey(User, related_name="receive_messages", on_delete=models.CASCADE, null=True, blank=True)  
    content = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # String representation of the Message model
    def __str__(self):
        return f'{self.sender} to {self.receiver}: {self.content}'

# Define the Room model for managing chat rooms
class Room(models.Model):
     sender = models.ForeignKey(User, related_name="room_sender", on_delete=models.CASCADE)      
     receiver = models.ForeignKey(User, related_name="room_receiver", on_delete=models.CASCADE)
     room_name = models.CharField(null=True, blank=True, max_length=200, unique=True)

# Define the Share model for sharing posts between users
class Share(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="share_sent")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="share_received")
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    expiration_timestamp = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=7))

    # String representation of the Share model
    def __str__(self):
        return f"{self.sender.username} shared a post with {self.receiver.username}"
