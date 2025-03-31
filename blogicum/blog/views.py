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

from .constants import POSTS_AMOUNT
from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post


User = get_user_model()


class PostsDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()

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

        context['form'] = CommentForm()
        context['comments'] = post.comments.all().filter(post=post)
        return context


class PostsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.get_username()}
        )


class PostsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        if post.author != self.request.user:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs.get('post_id')
            )
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class PostsDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create_post.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, **kwargs):
        return get_object_or_404(
            Post,
            pk=self.kwargs.get('post_id'),
        )

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author != self.request.user:
            return redirect(
                'blog:post_detail',
                self.kwargs.get('post_id')
            )
        return super().dispatch(request, *args, **kwargs)


class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_AMOUNT
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        return Post.objects.get_public_posts()


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
            Post.objects.get_public_posts()
            .filter(category=self.category.id)
            .order_by('-pub_date')
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
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


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(
                'blog:post_detail',
                post_id=kwargs.get('post_id')
            )
        return super().dispatch(request, *args, **kwargs)

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


class CommentDeleteView(LoginRequiredMixin, DeleteView):
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


class UserDetailView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_AMOUNT

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        queryset = Post.objects.filter(author=self.author)

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_published=True) & Q(pub_date__lte=timezone.now())
            )
        elif self.author != self.request.user:
            queryset = queryset.filter(
                Q(is_published=True) & Q(pub_date__lte=timezone.now())
            )
        else:
            queryset = queryset.filter(Q(author=self.request.user))

        return queryset.order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        context['user'] = self.request.user
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
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
