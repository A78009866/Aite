from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

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
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)