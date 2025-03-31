from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone
from core.models import BlogModel
from .constants import TITLE_MAX_LENGTH, TITLE_SHORT


User = get_user_model()


class Category(BlogModel):
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, '
                  'цифры, дефис и подчёркивание.'
    )

    class Meta(BlogModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:TITLE_SHORT]


class Location(BlogModel):
    name = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name='Название места'
    )

    class Meta(BlogModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:TITLE_SHORT]


class PostManager(models.Manager):
    def get_published(self, user=None):
        queryset = self.filter(pub_date__lte=timezone.now())
        if user and user.is_authenticated:
            queryset = queryset.filter(
                Q(is_published=True) | Q(author=user)
            )
        else:
            queryset = queryset.filter(is_published=True)
        return queryset

    def get_visible_posts(self, user=None):
        return self.get_published(user).filter(
            Q(category__isnull=True) | Q(category__is_published=True)
        )

    def get_posts_for_user(self, user=None):
        queryset = self.all()

        if not user or not user.is_authenticated:
            queryset = queryset.filter(
                Q(is_published=True) & 
                Q(pub_date__lte=timezone.now()) &
                (Q(category__isnull=True) | Q(category__is_published=True))
            )
        else:
            queryset = queryset.filter(
                Q(author=user) |
                (
                    Q(is_published=True) & 
                    Q(pub_date__lte=timezone.now()) &
                    (Q(category__isnull=True) | Q(category__is_published=True))
                )
            )

        return queryset.order_by('-pub_date')

    def get_author_posts(self, author):
        return self.filter(author=author).order_by('-pub_date')

    def get_public_posts(self):
        return self.filter(
            Q(is_published=True) &
            Q(pub_date__lte=timezone.now()) &
            (Q(category__isnull=True) | Q(category__is_published=True))
        ).order_by('-pub_date')


class Post(BlogModel):
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        null=False,
        verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время '
                  'в будущем — можно делать '
                  'отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
        related_query_name='post',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        related_name='posts',
        related_query_name='post',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts',
        related_query_name='post',
    )
    image = models.ImageField(
        'Фото',
        upload_to='birthdays_images',
        blank=True,
    )

    class Meta(BlogModel.Meta):
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title[:TITLE_SHORT]

    objects = PostManager()


class Comment(BlogModel):
    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )

    class Meta(BlogModel.Meta):
        ordering = ['created_at']
