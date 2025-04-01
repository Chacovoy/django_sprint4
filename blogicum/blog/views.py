from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
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


User = get_user_model()


class PostsDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = Post.objects.select_related(
                'author',
                'location',
                'category',
            ).prefetch_related(
                'comments__author',
            )

        post = get_object_or_404(
            queryset,
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


class AuthorMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostsCreateView(LoginRequiredMixin, AuthorMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.get_username()}
        )


class AuthorAccessMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        return post.author.id == self.request.user.id

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs.get('post_id')
        )


class PostsUpdateView(LoginRequiredMixin, AuthorAccessMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class PostsDeleteView(LoginRequiredMixin, AuthorAccessMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create_post.html'
    pk_url_kwarg = 'post_id'


class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_AMOUNT
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return Post.objects.get_published()


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


class CommentAuthorAccessMixin(UserPassesTestMixin):
    def test_func(self):
        comment = self.get_object()
        return comment.author.id == self.request.user.id

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs.get('post_id')
        )


class CommentUpdateView(
    LoginRequiredMixin, CommentAuthorAccessMixin, UpdateView
):
    model = Comment
    form_class = CommentForm

    def get_object(self, **kwargs):
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=get_object_or_404(
                Post,
                pk=self.kwargs.get('post_id')
            ),
            author=self.request.user
        )

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

    def get_object(self, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=post,
            author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class UserAccessMixin(UserPassesTestMixin):
    def test_func(self):
        return self.user.id == self.request.user.id

    def handle_no_permission(self):
        return redirect(
            'blog:profile',
            username=self.user.username
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
        context['request'] = self.request
        return context


class UserUpdateView(LoginRequiredMixin, UserAccessMixin, UpdateView):
    form_class = UserForm
    model = User
    template_name = 'blog/user.html'
    user = None

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(
            User,
            username=kwargs['username']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(
            User,
            username=self.user.get_username(),
        )

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.user.get_username()}
        )
