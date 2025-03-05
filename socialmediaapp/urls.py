from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import profile_view, edit_profile  # ✅ تأكد من استيراد profile_view



urlpatterns = [
    path('signup', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('home', views.home_view, name='home'),
    path('post/create/', views.post_create_view, name='post_create'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/dislike/', views.dislike_post, name='dislike_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('profile/<str:username>/', profile_view, name='profile'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
