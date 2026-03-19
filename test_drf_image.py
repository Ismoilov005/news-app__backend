import sys
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from news.serializers import NewsDetailSerializer
from users.serializers import UserSerializer
from news.models import News
from users.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile

user = CustomUser.objects.first()
if not user:
    user = CustomUser.objects.create(username="testuser", email="test@te.com")

avatar = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg')
user.avatar = avatar
user.save()

factory = APIRequestFactory()
request = factory.get('/api/users/')

serializer = UserSerializer(user, context={'request': request})
print("Avatar URL:", serializer.data['avatar'])
