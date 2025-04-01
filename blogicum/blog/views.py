from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blogicum.constants import POSTS_AMOUNT
from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post
from .mixins import (
    AuthorMixin,
    AuthorAccessMixin,
    CommentAuthorAccessMixin,
    PostMixin,
    UserAccessMixin,
)


User = get_user_model()


class PostsDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            Post.objects.select_related(
                'author',
                'location',
                'category',
            ).prefetch_related(
                'comments__author',
            ),
            pk=self.kwargs[self.pk_url_kwarg],
        )

        if post.author != self.request.user:
            if (
                not post.is_published
                or post.pub_date > timezone.now()
                or (post.category and not post.category.is_published)
            ):
                messages.error(
                    self.request,
                    "Вы не имеете доступа к этому посту."
                )
                raise Http404

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all()
        return context


class PostsCreateView(LoginRequiredMixin, AuthorMixin, PostMixin, CreateView):
    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.get_username()}
        )


class PostsUpdateView(
    LoginRequiredMixin, AuthorAccessMixin, PostMixin, UpdateView
):
    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class PostsDeleteView(
    LoginRequiredMixin, AuthorAccessMixin, PostMixin, DeleteView
):
    success_url = reverse_lazy('blog:index')


class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_AMOUNT
    pk_url_kwarg = 'post_id'
    queryset = Post.objects.get_published()


class CategoryListView(ListView):
    model = Category
    category = None
    template_name = 'blog/category_list.html'
    paginate_by = POSTS_AMOUNT

    def get_queryset(self):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return (
            Post.objects.get_published()
            .filter(category=self.category)
            .order_by('-pub_date')
        )


class CommentCreateView(LoginRequiredMixin, AuthorMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs.get('post_id')
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class CommentUpdateView(
    LoginRequiredMixin, CommentAuthorAccessMixin, UpdateView
):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class CommentDeleteView(
    LoginRequiredMixin,
    CommentAuthorAccessMixin,
    DeleteView
):
    model = Comment
    template_name = 'blog/comment_form.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class UserDetailView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_AMOUNT

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        if self.request.user.is_authenticated:
            return Post.objects.filter(
                Q(author=self.author) & (
                    Q(author=self.request.user) | Q(
                        is_published=True, pub_date__lte=timezone.now()
                    )
                )
            ).order_by('-pub_date')
        return Post.objects.filter(
            author=self.author,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    model = User
    template_name = 'blog/user.html'

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.object.get_username()}
        )
