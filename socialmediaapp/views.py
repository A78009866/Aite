from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Post, Like, Dislike, Comment
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

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

@login_required
def home_view(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})

@login_required
def post_create_view(request):
    if request.method == 'POST':
        content = request.POST['content']
        image = request.FILES.get('image')
        post = Post.objects.create(user=request.user, content=content, image=image)
        return redirect('home')
    return render(request, 'post_create.html')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likers.all():
        post.likers.remove(user)
        liked = False
    else:
        post.likers.add(user)
        liked = True

    return JsonResponse({"liked": liked, "like_count": post.likers.count()})

@login_required
def dislike_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not post.dislikes.filter(user=request.user).exists():
        Dislike.objects.create(user=request.user, post=post)
    return redirect('home')

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        comment = Comment.objects.create(user=request.user, post=post, content=content)
        return JsonResponse({
            'success': True,
            'comment_content': comment.content,
            'username': comment.user.username,
            'created_at': comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    return JsonResponse({'success': False})
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
            return redirect('profile')  # غير 'profile' إلى اسم صفحتك الشخصية
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import ProfileUpdateForm

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)  # جلب المستخدم المطلوب
    posts = Post.objects.filter(user=user).order_by('-created_at')  # جلب منشوراته فقط
    return render(request, 'profile.html', {'user': user, 'posts': posts})