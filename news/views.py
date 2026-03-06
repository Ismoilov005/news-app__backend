from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import News, Category, Tag, Comment, Like
from .serializers import (
    NewsListSerializer, NewsDetailSerializer, NewsWriteSerializer,
    CategorySerializer, TagSerializer, CommentSerializer
)
from .permissions import IsEditorOrReadOnly, IsOwnerOrAdmin


class NewsListView(generics.ListAPIView):
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'status', 'priority', 'is_featured', 'is_breaking']
    search_fields = ['title', 'summary', 'content', 'author__first_name']
    ordering_fields = ['published_at', 'views_count', 'likes_count', 'created_at']
    ordering = ['-published_at']

    def get_queryset(self):
        return News.objects.filter(
            status=News.Status.PUBLISHED
        ).select_related('author', 'category').prefetch_related('tags')


class NewsCreateView(generics.CreateAPIView):
    serializer_class = NewsWriteSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditorOrReadOnly]


class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    lookup_field = 'slug'
    permission_classes = [IsEditorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NewsDetailSerializer
        return NewsWriteSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self._increment_views_once(request, instance)  # ← o'zgartirildi
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _increment_views_once(self, request, news):
        """Bir session/IP dan kuniga 1 marta ko'rishni hisoblash"""
        session_key = f"viewed_news_{news.pk}"
        
        # Session asosida tekshirish
        if not request.session.get(session_key):
            news.increment_views()
            request.session[session_key] = True
            request.session.set_expiry(86400)  # 24 soat


class FeaturedNewsView(generics.ListAPIView):
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return News.objects.filter(
            status=News.Status.PUBLISHED, is_featured=True
        ).select_related('author', 'category')[:10]


class BreakingNewsView(generics.ListAPIView):
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return News.objects.filter(
            status=News.Status.PUBLISHED, is_breaking=True
        ).order_by('-published_at')[:5]


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsEditorOrReadOnly]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsEditorOrReadOnly]


class TagListView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsEditorOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        news = get_object_or_404(News, slug=self.kwargs['slug'])
        comment = serializer.save(author=self.request.user, news=news)
        News.objects.filter(pk=news.pk).update(comments_count=News.objects.get(pk=news.pk).comments.filter(is_approved=True).count())


class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        news = get_object_or_404(News, slug=slug, status=News.Status.PUBLISHED)
        like, created = Like.objects.get_or_create(news=news, user=request.user)

        if not created:
            like.delete()
            News.objects.filter(pk=news.pk).update(likes_count=news.likes.count() - 1)
            return Response({"liked": False, "likes_count": news.likes.count() - 1})

        News.objects.filter(pk=news.pk).update(likes_count=news.likes.count())
        return Response({"liked": True, "likes_count": news.likes.count()}, status=status.HTTP_201_CREATED)


class MyNewsView(generics.ListAPIView):
    serializer_class = NewsListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return News.objects.filter(author=self.request.user).order_by('-created_at')