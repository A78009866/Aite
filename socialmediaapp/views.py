from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Family, FamilyPost, Notification, Post, Like, Comment, CustomUser
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.utils import IntegrityError
from .models import Reels  # أضف هذا الاستيراد مع باقي الاستيرادات الأخرى

User = get_user_model()

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
        except IntegrityError as e:
            return render(request, 'signup.html', {'error': f'خطأ تقني: {str(e)}'})
        
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

import random
from django.db.models import Count

@login_required
def home_view(request):
    # جلب جميع المنشورات وتحويلها إلى قائمة
    posts = list(Post.objects.all())
    
    # جلب القصص من آخر 24 ساعة
    from datetime import timedelta
    from django.utils import timezone
    stories = Story.objects.filter(
        created_at__gte=timezone.now()-timedelta(hours=24)
    ).order_by('user', '-created_at').distinct('user')    
    # ترتيب المنشورات عشوائيًا
    random.shuffle(posts)

    # جعل المنشورات الجديدة (من المستخدم) في الأعلى
    if request.user.is_authenticated:
        user_posts = list(Post.objects.filter(user=request.user).order_by('-created_at'))
        posts = user_posts + [post for post in posts if post not in user_posts]

    return render(request, 'home.html', {
        'posts': posts,
        'stories': stories
    })

from django.shortcuts import render, redirect
from .models import Post
import cloudinary.uploader

def post_create(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        image = request.FILES.get("image")
        audio = request.FILES.get("audio")
        video = request.FILES.get("video")

        audio_url = None
        video_url = None

        # ✅ رفع الفيديو إلى كلوديناري
        if video:
            upload_result = cloudinary.uploader.upload(video, resource_type="video")
            video_url = upload_result.get("secure_url")
        
        # ✅ رفع الصوت إلى كلوديناري
        if audio:
            upload_result = cloudinary.uploader.upload(audio, resource_type="raw")
            audio_url = upload_result.get("secure_url")

        if not content and not image and not video_url and not audio_url:
            return render(request, "post_create.html", {"error": "يجب إضافة نص أو صورة أو صوت أو فيديو."})

        post = Post(
            user=request.user, 
            content=content, 
            video=video_url, 
            image=image, 
            audio=audio_url
        )
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
            post.likers.remove(user)
            liked = False
        else:
            post.likers.add(user)
            liked = True
            # إرسال إشعار للمستخدم صاحب المنشور
            if user != post.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=user,
                    notification_type='like',
                    post=post
                )

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
            
            # إرسال إشعار للمستخدم صاحب المنشور
            if request.user != post.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment
                )
            
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
    
    # تحديث جميع الرسائل كمقروءة ومشاهدة عند فتح المحادثة
    unread_messages = Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    )
    
    for msg in unread_messages:
        msg.mark_as_seen()  # استخدام الدالة الجديدة لتحديث الحقلين
    
    messages = Message.objects.filter(
        sender__in=[request.user, other_user], 
        receiver__in=[request.user, other_user]
    ).order_by("timestamp")

    return render(request, "chat.html", {
        "messages": messages, 
        "other_user": other_user
    })

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

        if not content:
            return JsonResponse({"error": "لا يمكن إرسال رسالة فارغة"}, status=400)

        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            is_read=False,
            seen_at=None
        )
        
        # إرسال إشعار للمستلم
        Notification.objects.create(
            recipient=receiver,
            sender=request.user,
            notification_type='message',
            content=content
        )

        return JsonResponse({
            "id": message.id,
            "sender": message.sender.username,
            "receiver": receiver.username,
            "content": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": message.is_read,
            "seen_at": None
        })


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
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": msg.is_read,
            "seen_at": msg.seen_at.strftime("%Y-%m-%d %H:%M:%S") if msg.seen_at else None
        }
        for msg in messages
    ], safe=False)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth import get_user_model
import datetime
from django.utils import timezone
import pytz  # أضف هذا الاستيراد
from django.utils.html import strip_tags
from django.http import Http404

User = get_user_model()

@login_required
def chat_list(request, username):
    try:
        current_user = request.user
        # جلب جميع المستخدمين ما عدا الحالي
        users = User.objects.exclude(id=current_user.id)
        
        query = request.GET.get('q', '')
        if query:
            users = users.filter(username__icontains=strip_tags(query))

        user_data = []
        for user in users:
            # جلب آخر رسالة مرسلة
            last_sent = Message.objects.filter(
                sender=current_user,
                receiver=user
            ).order_by('-timestamp').first()
            
            # جلب آخر رسالة مستلمة
            last_received = Message.objects.filter(
                sender=user,
                receiver=current_user
            ).order_by('-timestamp').first()

            # تحديد آخر رسالة بين الطرفين
            last_message = None
            if last_sent and last_received:
                last_message = last_sent if last_sent.timestamp > last_received.timestamp else last_received
            else:
                last_message = last_sent or last_received

            # تحديد إذا كانت هناك رسائل جديدة
            is_new = False
            if last_message and last_message.receiver == current_user and not last_message.is_read:
                is_new = True
                last_message.is_read = True
                last_message.save()

            user_data.append({
                'user': user,
                'last_message': strip_tags(last_message.content) if last_message else "لا توجد رسائل",
                'last_time': last_message.timestamp if last_message else None,
                'is_new': is_new
            })

        # ترتيب المحادثات حسب وقت آخر رسالة (الأحدث أولاً)
        user_data.sort(key=lambda x: x['last_time'] or timezone.datetime.min.replace(tzinfo=pytz.UTC), reverse=True)
        
        return render(request, 'chat_list.html', {
            'all_users': user_data,
            'current_user': current_user
        })

    except Exception as e:
        raise Http404(f"حدث خطأ: {str(e)}")

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
            # إرسال إشعار للمستخدم المتابَع
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow'
            )
            return JsonResponse({'status': 'success', 'action': 'follow', 'followers_count': user_to_follow.followers.count()})
        return JsonResponse({'status': 'error', 'message': 'لا يمكنك متابعة نفسك'}, status=400)
    
@login_required
def unfollow_user(request, username):
    if request.method == 'POST':
        user_to_unfollow = get_object_or_404(User, username=username)
        Follow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
        return JsonResponse({'status': 'success', 'action': 'unfollow', 'followers_count': user_to_unfollow.followers.count()})

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import cloudinary.uploader

@login_required
def change_profile_picture(request):
    if request.method == "POST" and request.FILES.get("profile_picture"):
        user = request.user
        image = request.FILES["profile_picture"]

        # ✅ رفع الصورة إلى Cloudinary
        upload_result = cloudinary.uploader.upload(image)
        user.profile_picture = upload_result["secure_url"]
        user.save()

        return JsonResponse({"success": True, "new_image_url": user.profile_picture})

    return JsonResponse({"success": False, "error": "⚠️ لم يتم رفع الصورة."})

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Story
from django.contrib.auth.decorators import login_required

@login_required
def add_story(request):
    if request.method == "POST":
        image = request.FILES.get("image")
        if image:
            story = Story.objects.create(user=request.user, image=image)
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

@login_required
def story_detail(request, story_id):
    story = Story.objects.get(id=story_id)
    return render(request, "story_detail.html", {"story": story})

from django.http import JsonResponse
from django.utils.timesince import timesince

def story_detail_json(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    return JsonResponse({
        'user': {
            'username': story.user.username,
            'profile_picture': story.user.profile_picture.url
        },
        'image': story.image.url,
        'time_ago': timesince(story.created_at) + ' ago'
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def delete_story(request, story_id):
    try:
        story = Story.objects.get(id=story_id, user=request.user)
        story.delete()
        return JsonResponse({'success': True})
    except Story.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'القصة غير موجودة أو لا تملك صلاحية الحذف'}, status=404)

        from django.http import JsonResponse
from .models import Follow

def get_followers(request, username):
    user = get_object_or_404(CustomUser, username=username)
    followers = Follow.objects.filter(followed=user).select_related('follower')
    
    followers_data = []
    for follow in followers:
        followers_data.append({
            'username': follow.follower.username,
            'profile_picture': follow.follower.profile_picture.url if follow.follower.profile_picture else '/media/profile_pics/default_profile.png'
        })
    
    return JsonResponse({
        'followers': followers_data
    })

from django.http import JsonResponse
from .models import Follow

def get_followers(request, username):
    user = get_object_or_404(CustomUser, username=username)
    followers = Follow.objects.filter(followed=user).select_related('follower')
    
    followers_data = []
    for follow in followers:
        followers_data.append({
            'username': follow.follower.username,
            'profile_picture': follow.follower.profile_picture.url if follow.follower.profile_picture else '/media/profile_pics/default_profile.png'
        })
    
    return JsonResponse({
        'followers': followers_data
    })

def get_following(request, username):
    user = get_object_or_404(CustomUser, username=username)
    following = Follow.objects.filter(follower=user).select_related('followed')
    
    following_data = []
    for follow in following:
        following_data.append({
            'username': follow.followed.username,
            'profile_picture': follow.followed.profile_picture.url if follow.followed.profile_picture else '/media/profile_pics/default_profile.png'
        })
    
    return JsonResponse({
        'following': following_data
    })

    # أضف هذه الدوال في views.py

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-created_at')[:10]
    notifications_data = []
    
    for notification in notifications:
        notifications_data.append({
            'id': notification.id,
            'sender': notification.sender.username,
            'sender_profile_picture': notification.sender.profile_picture.url,
            'type': notification.notification_type,
            'message': get_notification_message(notification), # type: ignore
            'post_id': notification.post.id if notification.post else None,
            'created_at': timesince(notification.created_at) + ' ago',
            'is_read': notification.is_read
        })
        notification.is_read = True
        notification.save()
    
    return JsonResponse({'notifications': notifications_data})

@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:20]
    notifications_data = []
    
    for notification in notifications:
        notification_data = {
            'id': notification.id,
            'sender': notification.sender.username,
            'sender_profile_picture': notification.sender.profile_picture.url,
            'type': notification.notification_type,
            'message': get_notification_message(notification),
            'content': notification.content,
            'post_id': notification.post.id if notification.post else None,
            'comment_id': notification.comment.id if notification.comment else None,
            'created_at': timesince(notification.created_at) + ' ago',
            'is_read': notification.is_read
        }
        notifications_data.append(notification_data)
    
    # تحديد عدد الإشعارات غير المقروءة
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })

def get_notification_message(notification):
    if notification.notification_type == 'like':
        return f"{notification.sender.username} أعجب بمنشورك"
    elif notification.notification_type == 'comment':
        return f"{notification.sender.username} علق على منشورك"
    elif notification.notification_type == 'follow':
        return f"{notification.sender.username} بدأ متابعتك"
    elif notification.notification_type == 'message':
        return f"رسالة جديدة من {notification.sender.username}"
    return "إشعار جديد"

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
def mark_all_notifications_as_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages

@login_required
def change_username(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_username = data.get("new_username", "").strip()
            
            if not new_username:
                return JsonResponse({"success": False, "error": "يجب إدخال اسم مستخدم جديد"})
                
            if CustomUser.objects.filter(username=new_username).exists():
                return JsonResponse({"success": False, "error": "اسم المستخدم هذا موجود بالفعل"})
                
            request.user.username = new_username
            request.user.save()
            return JsonResponse({"success": True})
            
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "طريقة غير مسموحة"})

@login_required
def change_password(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            current_password = data.get("current_password")
            new_password = data.get("new_password")
            
            user = request.user
            
            if not user.check_password(current_password):
                return JsonResponse({"success": False, "error": "كلمة المرور الحالية غير صحيحة"})
                
            if len(new_password) < 6:
                return JsonResponse({"success": False, "error": "يجب أن تكون كلمة المرور الجديدة 6 أحرف على الأقل"})
                
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # لمنع تسجيل الخروج بعد تغيير كلمة المرور
            
            return JsonResponse({"success": True})
            
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "طريقة غير مسموحة"})

    from django.http import JsonResponse
from .models import Comment

def post_comments(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = []
    
    for comment in post.comments.filter(parent__isnull=True):
        comments.append({
            'id': comment.id,
            'user': comment.user.username,
            'content': comment.content,
            'can_delete': comment.user == request.user,
            'replies': [
                {
                    'user': reply.user.username,
                    'content': reply.content
                } for reply in comment.replies.all()
            ]
        })
    
    return JsonResponse({'comments': comments})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if comment.user != request.user:
        return JsonResponse({'success': False, 'error': 'ليس لديك صلاحية حذف هذا التعليق'}, status=403)
    
    comment.delete()
    return JsonResponse({'success': True})

@login_required
def add_reply(request, comment_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()
            
            if not content:
                return JsonResponse({"success": False, "error": "تعليق فارغ"}, status=400)
            
            parent_comment = get_object_or_404(Comment, id=comment_id)
            reply = Comment.objects.create(
                user=request.user,
                post=parent_comment.post,
                content=content,
                parent=parent_comment
            )
            
            # إرسال إشعار لصاحب التعليق الأصلي
            if request.user != parent_comment.user:
                Notification.objects.create(
                    recipient=parent_comment.user,
                    sender=request.user,
                    notification_type='comment_reply',
                    post=parent_comment.post,
                    comment=reply
                )
            
            return JsonResponse({
                "success": True,
                "username": request.user.username,
                "content": reply.content
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    
    return JsonResponse({"success": False, "error": "طريقة غير مسموحة"}, status=405)

@login_required
def delete_reply(request, reply_id):
    reply = get_object_or_404(Comment, id=reply_id)
    
    if reply.user != request.user:
        return JsonResponse({'success': False, 'error': 'ليس لديك صلاحية حذف هذا الرد'}, status=403)
    
    reply.delete()
    return JsonResponse({'success': True})

@login_required
def delete_account(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            password = data.get("password")
            
            if not request.user.check_password(password):
                return JsonResponse({"success": False, "error": "كلمة المرور غير صحيحة"})
            
            # حذف جميع البيانات المرتبطة بالمستخدم
            request.user.delete()
            logout(request)
            
            return JsonResponse({"success": True, "redirect_url": reverse("login")})
            
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    
    return JsonResponse({"success": False, "error": "طريقة غير مسموحة"})

from django.contrib.auth.decorators import user_passes_test
from django.utils.html import strip_tags

@user_passes_test(lambda u: u.is_superuser)
def clean_malicious_content(request):
    from django.db.models import CharField
    from django.db.models.functions import Cast
    
    # تنظيف أسماء المستخدمين
    users = User.objects.annotate(
        str_username=Cast('username', CharField())
    ).filter(str_username__contains='<')
    
    for user in users:
        user.username = strip_tags(user.username)
        user.save()
    
    # تنظيف التعليقات
    comments = Comment.objects.filter(content__contains='<')
    for comment in comments:
        comment.content = strip_tags(comment.content)
        comment.save()
    
    return HttpResponse(f"تم تنظيف {users.count()} مستخدم و {comments.count()} تعليق")


import random
import string

@login_required
def create_family(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'يجب إدخال اسم العائلة'})
        
        # إنشاء كود عشوائي للعائلة
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        family = Family.objects.create(name=name, code=code, creator=request.user)
        family.members.add(request.user)
        
        return JsonResponse({'success': True, 'code': code, 'family_id': family.id})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def join_family(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        if not code:
            return JsonResponse({'success': False, 'error': 'يجب إدخال كود العائلة'})
        
        try:
            family = Family.objects.get(code=code)
            if request.user in family.members.all():
                return JsonResponse({'success': False, 'error': 'أنت بالفعل عضو في هذه العائلة'})
            
            family.members.add(request.user)
            return JsonResponse({'success': True, 'family_id': family.id})
        except Family.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'كود العائلة غير صحيح'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def family_detail(request, family_id):
    family = get_object_or_404(Family, id=family_id)
    if request.user not in family.members.all():
        return redirect('home')
    
    posts = FamilyPost.objects.filter(family=family).order_by('-created_at')
    
    return render(request, 'family_detail.html', {
        'family': family,
        'posts': posts,
        'is_creator': family.creator == request.user
    })

@login_required
def create_family_post(request, family_id):
    family = get_object_or_404(Family, id=family_id)
    if request.user not in family.members.all():
        return JsonResponse({'success': False, 'error': 'غير مسموح لك بالنشر في هذه العائلة'})
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        audio = request.FILES.get('audio')
        video = request.FILES.get('video')
        
        if not content and not image and not audio and not video:
            return JsonResponse({'success': False, 'error': 'يجب إضافة محتوى للمنشور'})
        
        post = FamilyPost.objects.create(
            family=family,
            user=request.user,
            content=content,
            image=image,
            audio=audio,
            video=video
        )
        
        return JsonResponse({'success': True, 'post_id': post.id})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def delete_family_post(request, family_id, post_id):
    post = get_object_or_404(FamilyPost, id=post_id, family_id=family_id)
    if post.user != request.user and post.family.creator != request.user:
        return JsonResponse({'success': False, 'error': 'ليس لديك صلاحية حذف هذا المنشور'})
    
    post.delete()
    return JsonResponse({'success': True})

@login_required
def family_list(request):
    families = request.user.families.all()
    return JsonResponse({
        'families': [
            {
                'id': family.id,
                'name': family.name,
                'code': family.code
            }
            for family in families
        ]
    })

@login_required
def like_family_post(request, family_id, post_id):
    if request.method == 'POST':
        post = get_object_or_404(FamilyPost, pk=post_id, family_id=family_id)
        user = request.user

        if user in post.likers.all():
            post.likers.remove(user)
            liked = False
        else:
            post.likers.add(user)
            liked = True
            # إرسال إشعار للمستخدم صاحب المنشور
            if user != post.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=user,
                    notification_type='like',
                    content=f"{user.username} أعجب بمنشورك في العائلة"
                )

        return JsonResponse({
            'liked': liked,
            'like_count': post.likers.count()
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def unlike_family_post(request, family_id, post_id):
    if request.method == 'POST':
        post = get_object_or_404(FamilyPost, pk=post_id, family_id=family_id)
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

@csrf_exempt
@login_required
def add_family_comment(request, family_id, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        content = data.get("content")
        
        if not content:
            return JsonResponse({"success": False, "error": "تعليق فارغ"}, status=400)
        
        try:
            post = FamilyPost.objects.get(id=post_id, family_id=family_id)
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            
            # إرسال إشعار للمستخدم صاحب المنشور
            if request.user != post.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type='comment',
                    content=f"{request.user.username} علق على منشورك في العائلة"
                )
            
            return JsonResponse({
                "success": True,
                "username": request.user.username,
                "content": comment.content
            })
        except FamilyPost.DoesNotExist:
            return JsonResponse({"success": False, "error": "المنشور غير موجود"}, status=404)
    
    return JsonResponse({"success": False, "error": "طلب غير صالح"}, status=400)


from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader
from datetime import timedelta

@login_required
def reels_list(request):
    # جلب الريلز من آخر أسبوع مع ترتيب حسب عدد المشاهدات والإعجابات
    reels = Reels.objects.filter(
        created_at__gte=timezone.now()-timedelta(days=7)
    ).annotate(
        likes_count=models.Count('likers')
    ).order_by('-views', '-likes_count', '-created_at')
    
    return render(request, 'reels/list.html', {
        'reels': reels,
        'is_reels_page': True  # للتمييز في القوالب
    })

@login_required
def upload_reel(request):
    if request.method == 'POST':
        video = request.FILES.get('video')
        caption = request.POST.get('caption', '').strip()
        music = request.POST.get('music', '').strip()
        
        if not video:
            return JsonResponse({'success': False, 'error': 'يجب اختيار فيديو'})
        
        try:
            # رفع الفيديو إلى Cloudinary
            upload_result = cloudinary.uploader.upload(
                video,
                resource_type="video",
                chunk_size=6000000,  # 6MB chunks for large files
                eager=[
                    {'width': 720, 'height': 1280, 'crop': 'fill', 'format': 'mp4'},
                    {'width': 480, 'height': 854, 'crop': 'fill', 'format': 'mp4'}
                ],
                eager_async=True
            )
            
            reel = Reels.objects.create(
                user=request.user,
                video=upload_result['secure_url'],
                caption=caption,
                music=music
            )
            
            return JsonResponse({
                'success': True,
                'reel_id': reel.id,
                'video_url': reel.video.url
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return render(request, 'reels/upload.html')

@login_required
def reel_detail(request, reel_id):
    reel = get_object_or_404(Reels, id=reel_id)
    
    # زيادة عدد المشاهدات عند عرض الريل
    if request.user != reel.user:
        reel.increment_views()
    
    
    # التحقق إذا كان المستخدم الحالي معجب بالريل
    is_liked = reel.likers.filter(id=request.user.id).exists()
    
    return render(request, 'reels/detail.html', {
        'reel': reel,
        'is_liked': is_liked,
        'is_reels_page': True
    })

@login_required
def like_reel(request, reel_id):
    if request.method == 'POST':
        reel = get_object_or_404(Reels, id=reel_id)
        user = request.user
        
        if user not in reel.likers.all():
            reel.likers.add(user)
            
            # إرسال إشعار للمستخدم صاحب الريل
            if user != reel.user:
                Notification.objects.create(
                    recipient=reel.user,
                    sender=user,
                    notification_type='like',
                    content=f"{user.username} أعجب بريلك",
                    post=None
                )
            
            return JsonResponse({
                'success': True,
                'action': 'like',
                'likes_count': reel.likers.count()
            })
        return JsonResponse({'success': False, 'error': 'تم الإعجاب بالفعل'})
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def unlike_reel(request, reel_id):
    if request.method == 'POST':
        reel = get_object_or_404(Reels, id=reel_id)
        user = request.user
        
        if user in reel.likers.all():
            reel.likers.remove(user)
            return JsonResponse({
                'success': True,
                'action': 'unlike',
                'likes_count': reel.likers.count()
            })
        return JsonResponse({'success': False, 'error': 'لم يتم الإعجاب بعد'})
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def delete_reel(request, reel_id):
    reel = get_object_or_404(Reels, id=reel_id, user=request.user)
    reel.delete()
    return JsonResponse({'success': True})

@login_required
def increment_reel_view(request, reel_id):
    if request.method == 'POST':
        reel = get_object_or_404(Reels, id=reel_id)
        if request.user != reel.user:
            reel.increment_views()
        return JsonResponse({'success': True, 'views': reel.views})
    return JsonResponse({'success': False})

