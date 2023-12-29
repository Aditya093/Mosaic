from django.urls import path
from django.conf import settings
from .views import *
from django.conf.urls.static import static
urlpatterns = [
  
    path("profile_list",profile_list,name="profile_list"),
    path("profile/<int:pk>", profile, name="profile"),
    path("post_list/<int:pk>",post_list,name="post_list"),
    path('chats/', GetAllUsers.as_view(), name='chats'),
    path('chat/<str:room_name>/',ChatRoom.as_view(), name='chat'),
    path('',Login,name="login"),
    path('login',Login,name="login"),
    path('register',register,name="register"),
    path('logout',Logout,name="logout"),
    path('upload',upload,name="upload"),
    path('like/', like_post, name='like_post'),
    path('shares/<int:post_id>/',share_post,name="share_post" ),
    path('share/<int:post_id>/',shared,name="share")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)