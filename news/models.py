from django.db import models
from django.utils.text import slugify
from users.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon nomi")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Teglar'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class News(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Qoralama'
        REVIEW = 'review', 'Ko\'rib chiqilmoqda'
        PUBLISHED = 'published', 'Nashr etilgan'
        ARCHIVED = 'archived', 'Arxivlangan'

    class Priority(models.TextChoices):
        LOW = 'low', 'Past'
        NORMAL = 'normal', 'Oddiy'
        HIGH = 'high', 'Yuqori'
        BREAKING = 'breaking', 'Tezkor xabar'

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    summary = models.TextField(max_length=500, help_text="Qisqacha tavsif (maks 500 belgi)")
    content = models.TextField()
    image = models.ImageField(upload_to='news/images/%Y/%m/', blank=True, null=True)
    image_caption = models.CharField(max_length=200, blank=True)

    author = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True,
        related_name='news', verbose_name='Muallif'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='news', verbose_name='Kategoriya'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='news')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)

    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    source = models.CharField(max_length=200, blank=True, help_text="Manba nomi")
    source_url = models.URLField(blank=True, help_text="Manba URL")

    is_featured = models.BooleanField(default=False, help_text="Bosh sahifada ko'rsatish")
    is_breaking = models.BooleanField(default=False, help_text="Tezkor xabar")

    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Yangilik'
        verbose_name_plural = 'Yangiliklar'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def increment_views(self):
        News.objects.filter(pk=self.pk).update(views_count=models.F('views_count') + 1)


class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField(max_length=1000)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Izoh'
        verbose_name_plural = 'Izohlar'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.get_full_name()} - {self.news.title[:50]}"


class Like(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['news', 'user']
        verbose_name = 'Like'
        verbose_name_plural = 'Likelar'