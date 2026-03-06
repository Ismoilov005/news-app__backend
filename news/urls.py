from django.urls import path
from .views import (
    NewsListView, NewsCreateView, NewsDetailView,
    FeaturedNewsView, BreakingNewsView,
    CategoryListView, CategoryDetailView,
    TagListView,
    CommentCreateView, LikeToggleView,
    MyNewsView,
)

urlpatterns = [
    # ── Yangiliklar (aniq yo'llar AVVAL) ──────────────────
    path('', NewsListView.as_view(), name='news-list'),
    path('create/', NewsCreateView.as_view(), name='news-create'),
    path('featured/', FeaturedNewsView.as_view(), name='news-featured'),
    path('breaking/', BreakingNewsView.as_view(), name='news-breaking'),
    path('my/', MyNewsView.as_view(), name='my-news'),

    # ── Kategoriyalar (slug dan OLDIN bo'lishi SHART) ─────
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category-detail'),

    # ── Teglar ────────────────────────────────────────────
    path('tags/', TagListView.as_view(), name='tag-list'),

    # ── Slug bilan (ENG OXIRIDA bo'lishi SHART) ───────────
    path('<slug:slug>/', NewsDetailView.as_view(), name='news-detail'),
    path('<slug:slug>/like/', LikeToggleView.as_view(), name='news-like'),
    path('<slug:slug>/comments/', CommentCreateView.as_view(), name='news-comment'),
]