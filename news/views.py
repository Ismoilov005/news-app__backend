from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q

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
    queryset = News.objects.select_related('author', 'category').prefetch_related('tags')
    lookup_field = 'slug'
    permission_classes = [IsEditorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return NewsDetailSerializer
        return NewsWriteSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self._increment_views_once(request, instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def _increment_views_once(self, request, news):
        """
        Bir foydalanuvchi / IP 24 soat ichida faqat 1 marta view hisoblanadi.
        select_for_update() bilan race condition oldini oladi.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')

        from datetime import timedelta
        from django.db import transaction
        from .models import NewsViewLog

        time_threshold = timezone.now() - timedelta(hours=24)

        with transaction.atomic():
            if request.user.is_authenticated:
                # Autentifikatsiya qilingan foydalanuvchi uchun user bo'yicha tekshirish
                already_viewed = NewsViewLog.objects.select_for_update().filter(
                    news=news,
                    user=request.user,
                    viewed_at__gte=time_threshold
                ).exists()
            else:
                # Anonim foydalanuvchi uchun IP bo'yicha tekshirish
                already_viewed = NewsViewLog.objects.select_for_update().filter(
                    news=news,
                    user__isnull=True,
                    ip_address=ip,
                    viewed_at__gte=time_threshold
                ).exists()

            if not already_viewed:
                NewsViewLog.objects.create(
                    news=news,
                    user=request.user if request.user.is_authenticated else None,
                    ip_address=ip
                )
                news.increment_views()


class FeaturedNewsView(generics.ListAPIView):
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return News.objects.filter(
            status=News.Status.PUBLISHED, is_featured=True
        ).select_related('author', 'category').prefetch_related('tags')[:10]


class BreakingNewsView(generics.ListAPIView):
    serializer_class = NewsListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return News.objects.filter(
            status=News.Status.PUBLISHED, is_breaking=True
        ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')[:5]


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(is_active=True).annotate(
        news_count_annotated=Count('news', filter=Q(news__status=News.Status.PUBLISHED))
    )
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


class CommentCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(
            news__slug=self.kwargs['slug'],
            is_approved=True
        ).select_related('author').order_by('-created_at')

    def perform_create(self, serializer):
        news = get_object_or_404(News, slug=self.kwargs['slug'])
        serializer.save(author=self.request.user, news=news)
        News.objects.filter(pk=news.pk).update(
            comments_count=News.objects.get(pk=news.pk).comments.filter(is_approved=True).count()
        )


class LikeToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        from django.db import transaction

        with transaction.atomic():
            news = get_object_or_404(
                News.objects.select_for_update(),
                slug=slug,
                status=News.Status.PUBLISHED
            )

            like, created = Like.objects.get_or_create(news=news, user=request.user)

            if not created:
                # Like mavjud edi → o'chirish (unlike)
                like.delete()
                count = news.likes.count()
                News.objects.filter(pk=news.pk).update(likes_count=count)
                return Response({
                    "is_liked": False,      # ← frontend "is_liked" kutadi
                    "likes_count": count
                })

            # Yangi like qo'shildi
            count = news.likes.count()
            News.objects.filter(pk=news.pk).update(likes_count=count)
            return Response({
                "is_liked": True,           # ← frontend "is_liked" kutadi
                "likes_count": count
            }, status=status.HTTP_201_CREATED)


class MyNewsView(generics.ListAPIView):
    serializer_class = NewsListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return News.objects.filter(
            author=self.request.user
        ).select_related('author', 'category').prefetch_related('tags').order_by('-created_at')