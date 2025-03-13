from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import search_view, post_detail
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('post/create/', views.post_create_view, name='post_create'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:id>/like/', views.like_post, name='like_post'),
    path('post/<int:id>/unlike/', views.unlike_post, name='unlike_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('splash/', views.splash, name='splash'),
    path("search/", search_view, name="search"),
    path("post/<int:post_id>/", post_detail, name="post_detail"),
    path('change-password/', views.custom_password_change, name='custom_password_change'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)