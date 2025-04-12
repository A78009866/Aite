from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import search_view, post_detail
from django.contrib.auth import views as auth_views
from .views import follow_user, unfollow_user
from .views import change_profile_picture
from .views import add_story, story_detail
from .views import delete_story
from .views import get_followers, get_following
from .views import change_username, change_password
from .views import clean_malicious_content

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
    path('story/add/', add_story, name='add_story'),
    path('story/<int:story_id>/', story_detail, name='story_detail'),
    path('story/<int:story_id>/json/', views.story_detail_json, name='story_detail_json'),
    path('story/<int:story_id>/delete/', delete_story, name='delete_story'),
    path('get_followers/<str:username>/', get_followers, name='get_followers'),
    path('get_following/<str:username>/', get_following, name='get_following'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/mark_all_read/', views.mark_all_notifications_as_read, name='mark_all_notifications_as_read'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('change_username/', change_username, name='change_username'),
    path('change_password/', change_password, name='change_password'),
    path('post/<int:post_id>/comments/', views.post_comments, name='post_comments'),
path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
path('comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
path('reply/<int:reply_id>/delete/', views.delete_reply, name='delete_reply'),
path('delete_account/', views.delete_account, name='delete_account'),
    path('admin/clean-html/', clean_malicious_content, name='clean_html'),
path('family/create/', views.create_family, name='create_family'),
path('family/join/', views.join_family, name='join_family'),
path('family/<int:family_id>/', views.family_detail, name='family_detail'),
path('family/<int:family_id>/post/create/', views.create_family_post, name='create_family_post'),
path('family/<int:family_id>/post/<int:post_id>/delete/', views.delete_family_post, name='delete_family_post'),
path('family/list/', views.family_list, name='family_list'),
path('reels/', views.reels_view, name='reels'),
path('reel/<int:reel_id>/like/', views.like_reel, name='like_reel'),
path('reels/create/', views.create_reel, name='create_reel'),
path('family/<int:family_id>/post/<int:post_id>/like/', views.like_family_post, name='like_family_post'),
path('family/<int:family_id>/post/<int:post_id>/unlike/', views.unlike_family_post, name='unlike_family_post'),
path('family/<int:family_id>/post/<int:post_id>/comment/', views.add_family_comment, name='add_family_comment'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)