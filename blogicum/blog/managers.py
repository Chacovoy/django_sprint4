from django.db import models
from django.utils import timezone


class PostManager(models.Manager):
    def get_published(self, user=None):
        queryset = self.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__isnull=True
        ) | self.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

        if user and user.is_authenticated:
            queryset = queryset | self.filter(author=user)

        return queryset.order_by('-pub_date')

    def get_user_posts(self, user=None, profile_user=None):
        return self.filter(
            models.Q(author=user) | models.Q(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__isnull=True,
                author=profile_user
            ) | models.Q(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True,
                author=profile_user
            )
        ).order_by('-pub_date')
