from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

from .forms import PostForm
from .models import Post


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


class UserAccessMixin(UserPassesTestMixin):
    def test_func(self):
        return self.user.id == self.request.user.id

    def handle_no_permission(self):
        return redirect(
            'blog:profile',
            username=self.user.username
        ) 