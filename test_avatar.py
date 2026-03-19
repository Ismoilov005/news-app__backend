import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from users.models import CustomUser
user = CustomUser.objects.first()
if user and user.avatar:
    print(user.avatar.url)
else:
    print("No avatar found")
from news.models import News
news = News.objects.exclude(image='').first()
if news and news.image:
    print(news.image.url)
else:
    print("No news image found")
