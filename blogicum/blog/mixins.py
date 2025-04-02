from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from .forms import PostForm
from .models import Comment, Post


class AuthorMixin:
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create_post.html'
    pk_url_kwarg = 'post_id'


class AuthorAccessMixin(UserPassesTestMixin):
    def test_func(self):
        post = self.get_object()
        return post.author.id == self.request.user.id

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs.get('post_id')
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


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs.get('post_id')}
        )


class UserAccessMixin:
    def test_func(self):
        return self.request.user == self.user

    def handle_no_permission(self):
        return redirect('blog:profile', username=self.user.username)
