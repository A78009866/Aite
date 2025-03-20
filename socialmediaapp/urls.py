from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import search_view, post_detail
from django.contrib.auth import views as auth_views
from .views import follow_user, unfollow_user
from .views import change_profile_picture

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('post/create/', views.post_create, name='post_create'),
    path('change-profile-picture/', change_profile_picture, name='change_profile_picture'),

    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:id>/like/', views.like_post, name='like_post'),
    path('post/<int:id>/unlike/', views.unlike_post, name='unlike_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('splash/', views.splash, name='splash'),
    path("search/", search_view, name="search"),
    path("post/<int:post_id>/", post_detail, name="post_detail"),
    path('change-password/', views.custom_password_change, name='custom_password_change'),
    path("chat/<str:username>/", views.chat_view, name="chat"),
    path("send-message/", views.send_message, name="send_message"),
    path("chat/<str:username>/get-messages/", views.get_messages, name="get_messages"),
    path('chat/list/<str:username>/', views.chat_list, name='chat_list'),  # يتوقع وسيطة username
    path('follow/<str:username>/', follow_user, name='follow_user'),
    path('unfollow/<str:username>/', unfollow_user, name='unfollow_user'),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)