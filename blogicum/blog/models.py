from django.contrib.auth import get_user_model
from django.db import models

from core.models import BlogModel
from blogicum.constants import TITLE_MAX_LENGTH, TITLE_SHORT
from .managers import PostManager


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

    objects = PostManager()

    class Meta(BlogModel.Meta):
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title[:TITLE_SHORT]


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
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']
