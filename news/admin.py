from django.contrib import admin
from django.utils.html import format_html
from .models import News, Category, Tag, Comment, Like


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'priority',
                    'views_count', 'likes_count', 'is_featured', 'published_at']
    list_filter = ['status', 'priority', 'category', 'is_featured', 'is_breaking']
    search_fields = ['title', 'summary', 'author__email']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    ordering = ['-created_at']
    list_per_page = 30

    fieldsets = (
        ('Asosiy', {'fields': ('title', 'slug', 'summary', 'content')}),
        ('Media', {'fields': ('image', 'image_caption')}),
        ('Tasnif', {'fields': ('author', 'category', 'tags')}),
        ('Holat', {'fields': ('status', 'priority', 'is_featured', 'is_breaking', 'published_at')}),
        ('Manba', {'fields': ('source', 'source_url')}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" />', obj.image.url)
        return "—"
    image_preview.short_description = 'Rasm'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'news', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Tanlangan izohlarni tasdiqlash"