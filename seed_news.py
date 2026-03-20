import os
import django
from django.utils.text import slugify
from django.utils import timezone
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from news.models import News, Category
from django.contrib.auth import get_user_model

User = get_user_model()
author = User.objects.first()
if not author:
    author = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

categories = ['O\'zbekiston', 'Jahon', 'Sport', 'Iqtisodiyot', 'Texnologiya']
category_objs = []
for cat_name in categories:
    cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'slug': slugify(cat_name)})
    category_objs.append(cat)

news_data = [
    {
        "title": "Toshkentda yangi texnopark ishga tushdi",
        "summary": "Poytaxtimizda zamonaviy IT kompaniyalar uchun mo'ljallangan yirik texnopark o'z ishini boshladi.",
        "content": "<p>Toshkent shahrida axborot texnologiyalari sohasida faoliyat yurituvchi mahalliy va xorijiy kompaniyalar uchun barcha qulayliklarga ega yangi IT-park foydalanishga topshirildi. Uning maydoni 10 gektardan ortiq.</p>",
    },
    {
        "title": "O'zbekiston terma jamoasi Osiyo chempionatida g'olib bo'ldi",
        "summary": "Futbol bo'yicha yoshlar o'rtasida o'tkazilgan musobaqada vakillarimiz oltin medallarni qo'lga kiritdi.",
        "content": "<p>Qit'a birinchiligining final bosqichida qatnashgan O'zbekiston yoshlar terma jamoasi hal qiluvchi bahsda raqiblarini mag'lub etib, Osiyo chempioni degan sharafli nomga sazovor bo'ldi.</p>",
    },
    {
        "title": "Dollarning rasmiy kursi yana oshdi",
        "summary": "Markaziy bank xorijiy valyutalarning so'mga nisbatan yangi qiymatini e'lon qildi.",
        "content": "<p>O'zbekiston Respublikasi Markaziy banki joriy yilning shu haftasi uchun xorijiy valyutalarning so'mga nisbatan rasmiy kurslarini e'lon qildi. Dollarning qiymati biroz oshgani kuzatildi.</p>",
    },
    {
        "title": "Yangi smartfon modeli taqdim etildi",
        "summary": "Jahonning yetakchi texnologiya kompaniyasi o'zining eng so'nggi flagman smartfonini namoyish qildi.",
        "content": "<p>Texnologiya ishqibozlari uzoq kutgan yangi avlod smartfoni nihoyat taqdim etildi. Qurilma ilg'or kameralar, kuchli protsessor va uzaytirilgan batareya quvvati bilan jihozlangan.</p>",
    },
    {
        "title": "Xalqaro anjuman o'z ishini boshladi",
        "summary": "Toshkent shahrida atrof-muhitni muhofaza qilish masalalariga bag'ishlangan yirik xalqaro forum ochildi.",
        "content": "<p>Dunyodagi eng dolzarb muammolardan biri bo'lgan ekologik vaziyat va iqlim o'zgarishi masalalari muhokama qilinadigan yirik xalqaro anjuman poytaxtimizda o'z ishini boshladi.</p>",
    }
]

titles_bases = [
    "Iqtisodiyotda yangi islohotlar e'lon qilindi",
    "Sportchilarimiz xalqaro turnirda g'olib bo'ldi",
    "Yangi ta'lim dasturi joriy etilmoqda",
    "Markaziy Osiyo mamlakatlari rahbarlari uchrashdi",
    "Tibbiyot sohasida muhim kashfiyot qilindi",
    "Yirik ishlab chiqarish zavodi ochildi",
    "Elektr transport vositalari ishlab chiqarish kengaytiriladi",
    "Yangi temir yo'l liniyasi qurilishi boshlandi",
    "Hududlarda yangi ish o'rinlari yaratildi",
    "O'zbekistonlik olim yirik xalqaro mukofotga sazovor bo'ldi",
    "Turizm sohasida yangi loyihalar tasdiqlandi",
    "Sayyohlar oqimi sezilarli darajada oshdi",
    "Qishloq xo'jaligida yangi texnologiyalar qo'llanilmoqda",
    "Xorijiy investorlar bilan yirik shartnomalar imzolandi",
    "Qayta tiklanuvchi energiya manbalaridan foydalanish ko'paymoqda",
    "Yangi avtotrassaning birinchi qismi foydalanishga topshirildi",
    "Suv resurslarini tejash bo'yicha yangi chora-tadbirlar qabul qilindi",
    "Milliy kinematografiya sohasiga katta investitsiya jalb etildi",
    "Qurilish sohasida yangi standartlar kuchga kirdi",
    "Yoshlar tadbirkorligini qo'llab-quvvatlash jamg'armasi tashkil etildi"
]

for title in titles_bases:
    news_data.append({
        "title": title,
        "summary": f"{title} bo'yicha batafsil ma'lumotlar e'lon qilindi va bu borada qator o'zgarishlar kutilmoqda.",
        "content": f"<p>{title} haqidagi xabar barchani quvontirdi. Mutaxassislar bu jarayonning ijobiy natijalarini kutishmoqda. Loyiha doirasida ko'plab amaliy tadbirlar amalga oshiriladi.</p>"
    })

for i, data in enumerate(news_data):
    news, created = News.objects.get_or_create(
        title=data["title"],
        defaults={
            "slug": slugify(data["title"]) + f"-{i}",
            "summary": data["summary"],
            "content": data["content"],
            "category": random.choice(category_objs),
            "author": author,
            "is_breaking": random.choice([True, False, False, False]),
            "is_featured": random.choice([True, False, False]),
        }
    )
    if created:
        print(f"Created news: {news.title}")
    else:
        print(f"Already exists: {news.title}")

print(f"Successfully ensured {len(news_data)} news items exist!")
