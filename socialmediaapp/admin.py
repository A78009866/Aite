from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import CustomUser, Post, Comment

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ('username',)
    list_filter = ('is_staff', 'is_superuser')
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if '<' in search_term or '>' in search_term:
            self.message_user(request, 'تم تصفية المستخدمين الذين يحتوي اسمهم على HTML', level='WARNING')
        return queryset, use_distinct

admin.site.register(Post)
admin.site.register(Comment)