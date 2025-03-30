from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, PasswordChangeForm, PostForm, UserForm
from .models import Category, Comment, Post, User
from .utils import filter_published, select_post_objects

POSTS_AMOUNT: int = 10


class PostsDetailView(DetailView):
    model = Post
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        if post.author != self.request.user and not post.is_published:
            raise Http404
        context['form'] = CommentForm()
        context['comments'] = Comment.objects.prefetch_related(
            'post'
        ).filter(
            post=post
        )
        return context


class PostsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={
                'username': self.request.user.get_username()
            }
        )


class PostsUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'

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

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_id')}
        )


class PostsDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create_post.html'

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
    paginate_by: int = POSTS_AMOUNT

    def get_queryset(self):
        return filter_published(
            select_post_objects(Post).filter(
                category__is_published=True,
                pub_date__lte=datetime.now())
        ).order_by('-pub_date')


class CategoryListView(ListView):
    model = Category
    category = None
    template_name = 'blog/category_list.html'
    paginate_by: int = POSTS_AMOUNT

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            slug=kwargs['category_slug'],
            is_published=True,
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return filter_published(select_post_objects(Post).filter(
            category=self.category.id,
            pub_date__lte=datetime.now(),
        )).order_by('-pub_date')


class CommentCreateView(LoginRequiredMixin, CreateView):
    blog_post = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.blog_post = get_object_or_404(
            Post,
            pk=kwargs.get('post_id')
        )
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=Post.objects.get(pk=self.kwargs.get('post_id')),
            author=self.request.user)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.blog_post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_id')}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('blog:post_detail', post_id=obj.id)
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        return get_object_or_404(
            Comment,
            pk=self.kwargs.get('comment_id'),
            post=Post.objects.get(pk=self.kwargs.get('post_id')),
            author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_id')}
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
            author=self.request.user)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs.get('post_id')}
        )


class UserDetailView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by: int = POSTS_AMOUNT

    def get_queryset(self):
        self.author = get_object_or_404(
            User,
            username=self.kwargs['username']
        )

        if self.author != self.request.user:
            return filter_published(select_post_objects(Post).filter(
                author=self.author,
            )).order_by(
                '-pub_date')

        return select_post_objects(Post).filter(
            author=self.author
        ).order_by('-pub_date')

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


class UserPasswordUpdateView(UserUpdateView):
    form_class = PasswordChangeForm
    model = User
    template_name = 'registration/password_reset_form.html'
