from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Post, Like, Comment, CustomUser
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.utils import IntegrityError

User = get_user_model

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password_confirmation = request.POST['password_confirmation']

        if password != password_confirmation:
            return render(request, 'signup.html', {'error': 'كلمة المرور غير متطابقة.'})

        # ✅ التحقق مما إذا كان اسم المستخدم مستخدمًا بالفعل
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'اسم المستخدم مستخدم بالفعل. اختر اسمًا آخر.'})

        try:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            login(request, user)  # تسجيل الدخول تلقائيًا بعد إنشاء الحساب
            return redirect('home')
        except IntegrityError:
            return render(request, 'signup.html', {'error': 'حدث خطأ أثناء التسجيل. حاول مرة أخرى.'})

    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

from django.db.models import Count

@login_required
def home_view(request):
    posts = Post.objects.annotate(likes_count=Count('likers')).order_by('-likes_count', '-created_at')
    
    # إضافة حالة المتابعة لكل منشور
    for post in posts:
        post.is_following = Follow.objects.filter(follower=request.user, followed=post.user).exists()
    
    return render(request, 'home.html', {'posts': posts})

from django.shortcuts import render, redirect
from .models import Post
import cloudinary.uploader

def post_create(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        image = request.FILES.get("image")
        audio = request.FILES.get("audio")
        video = request.FILES.get("video")  # ✅ استقبال الفيديو

        if video:
            upload_result = cloudinary.uploader.upload(video, resource_type="video")  # ✅ رفع الفيديو كـ فيديو
            video_url = upload_result.get("secure_url")
        else:
            video_url = None
        if not content and not image and not video and not audio:
            return render(request, "post_create.html", {"error": "يجب إضافة نص أو صورة أو صوت أو فيديو."})

        post = Post(user=request.user, content=content, video=video_url, image=image, audio=audio)
        post.save()

        return redirect("home")

    return render(request, "post_create.html")


from django.http import JsonResponse

@login_required
def like_post(request, id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=id)
        user = request.user

        if user in post.likers.all():
            # إذا كان المستخدم قد أعجب بالمنشور بالفعل، قم بإزالة الإعجاب
            post.likers.remove(user)
            liked = False
        else:
            # إذا لم يكن المستخدم قد أعجب بالمنشور، قم بإضافة الإعجاب
            post.likers.add(user)
            liked = True

        return JsonResponse({
            'liked': liked,
            'like_count': post.likers.count()
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def unlike_post(request, id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=id)
        user = request.user

        if user in post.likers.all():
            post.likers.remove(user)
            liked = False
        else:
            liked = True

        return JsonResponse({
            'liked': liked,
            'like_count': post.likers.count()
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Post, Comment

@csrf_exempt
def add_comment(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")
        
        if not content:
            return JsonResponse({"success": False, "error": "تعليق فارغ"}, status=400)
        
        try:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            
            return JsonResponse({
                "success": True,
                "username": request.user.username,
                "content": comment.content
            })
        except Post.DoesNotExist:
            return JsonResponse({"success": False, "error": "المنشور غير موجود"}, status=404)
    
    return JsonResponse({"success": False, "error": "طلب غير صالح"}, status=400)

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user == request.user:
        post.delete()
    return redirect('home')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)  # ✅ تمرير اسم المستخدم
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ProfileUpdateForm

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser as User

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=user).order_by('-created_at')
    
    # التحقق مما إذا كان المستخدم الحالي يتابع المستخدم المعروض
    is_following = Follow.objects.filter(follower=request.user, followed=user).exists()
    
    return render(request, 'profile.html', {
        'user': user,
        'posts': posts,
        'is_following': is_following,  # تمرير حالة المتابعة
    })
from django.shortcuts import render

def splash(request):
    return render(request, 'splash.html')

from django.http import JsonResponse
from .models import CustomUser as User
from .models import Post

def search_view(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"users": [], "posts": []})

    users = User.objects.filter(username__icontains=query).values("username")  # ✅ تعديل لاستخدام CustomUser
    posts = Post.objects.filter(content__icontains=query).values("id", "content")

    return JsonResponse({
        "users": list(users),
        "posts": list(posts)
    })

from django.shortcuts import render, get_object_or_404
from .models import Post

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, "post_detail.html", {"post": post})

from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomPasswordChangeForm

@login_required
def custom_password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  # تأمين استمرار الجلسة بعد تغيير كلمة المرور
            messages.success(request, "تم تغيير كلمة المرور بنجاح!")
            return redirect('profile', username=request.user.username)  # إعادة التوجيه إلى صفحة البروفايل
        else:
            messages.error(request, "حدث خطأ. تأكد من صحة البيانات المدخلة.")
    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'custom_password_change.html', {'form': form})


from .models import Message
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        sender__in=[request.user, other_user], 
        receiver__in=[request.user, other_user]
    ).order_by("timestamp")

    return render(request, "chat.html", {"messages": messages, "other_user": other_user})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, CustomUser
import json
from django.db import models

@login_required
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        receiver = get_object_or_404(CustomUser, username=data["receiver"])
        content = data["content"].strip()

        if not content:  # تجنب إرسال رسائل فارغة
            return JsonResponse({"error": "لا يمكن إرسال رسالة فارغة"}, status=400)

        message = Message.objects.create(sender=request.user, receiver=receiver, content=content)

        return JsonResponse({
            "id": message.id,
            "sender": message.sender.username,
            "receiver": receiver.username,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse({"error": "طلب غير صالح"}, status=400)


@login_required
def get_messages(request, username):
    """جلب الرسائل بين المستخدم الحالي والمستخدم الآخر"""
    other_user = get_object_or_404(CustomUser, username=username)
    
    messages = Message.objects.filter(
        (models.Q(sender=request.user, receiver=other_user) | 
         models.Q(sender=other_user, receiver=request.user))
    ).order_by("timestamp")

    return JsonResponse([
        {
            "id": msg.id,
            "sender": msg.sender.username,
            "receiver": msg.receiver.username,
            "content": msg.content,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for msg in messages
    ], safe=False)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat_list(request, username):
    # جلب جميع المستخدمين ما عدا المستخدم الحالي
    all_users = User.objects.exclude(id=request.user.id)
    
    context = {
        'all_users': all_users,  # إرسال جميع المستخدمين إلى القالب
    }
    return render(request, 'chat_list.html', context)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def chat(request, username):
    # جلب المستخدم الذي تريد المحادثة معه
    other_user = get_object_or_404(User, username=username)
    
    context = {
        'other_user': other_user,
    }
    return render(request, 'chat.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Follow, CustomUser as User
from django.http import JsonResponse
from django.http import JsonResponse

@login_required
def follow_user(request, username):
    if request.method == 'POST':
        user_to_follow = get_object_or_404(User, username=username)
        if request.user != user_to_follow:
            Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
            return JsonResponse({'status': 'success', 'action': 'follow', 'followers_count': user_to_follow.followers.count()})
        return JsonResponse({'status': 'error', 'message': 'لا يمكنك متابعة نفسك'}, status=400)

@login_required
def unfollow_user(request, username):
    if request.method == 'POST':
        user_to_unfollow = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
        return JsonResponse({'status': 'success', 'action': 'unfollow', 'followers_count': user_to_unfollow.followers.count()})

        