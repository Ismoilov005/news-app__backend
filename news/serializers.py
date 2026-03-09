from rest_framework import serializers
from .models import News, Category, Tag, Comment, Like
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    news_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'is_active', 'news_count']

    def get_news_count(self, obj):
        if hasattr(obj, 'news_count_annotated'):
            return obj.news_count_annotated
        return obj.news.filter(status=News.Status.PUBLISHED).count()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'parent', 'replies', 'is_approved', 'created_at']
        read_only_fields = ['id', 'author', 'is_approved', 'created_at']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True).data
        return []


class NewsListSerializer(serializers.ModelSerializer):
    """Ro'yxat uchun yengil serializer"""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = [
            'id', 'title', 'slug', 'summary', 'image', 'author',
            'category', 'tags', 'status', 'priority', 'views_count',
            'likes_count', 'comments_count', 'is_featured', 'is_breaking',
            'published_at', 'created_at'
        ]


class NewsDetailSerializer(serializers.ModelSerializer):
    """To'liq detail uchun"""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = '__all__'

    def get_comments(self, obj):
        top_level = obj.comments.filter(parent=None, is_approved=True)
        return CommentSerializer(top_level, many=True).data

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False


class NewsWriteSerializer(serializers.ModelSerializer):
    """Yaratish va tahrirlash uchun"""
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True, source='tags', required=False
    )

    class Meta:
        model = News
        exclude = ['views_count', 'likes_count', 'comments_count', 'author']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)