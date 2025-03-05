from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import login_view, logout_view, signup_view, edit_profile, profile_view, home_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home_view, name='home'),  # ✅ جعل الصفحة الرئيسية تعمل على "/"
    path('signup/', views.signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('post/create/', views.post_create_view, name='post_create'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/dislike/', views.dislike_post, name='dislike_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('profile/<str:username>/', profile_view, name='profile'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
