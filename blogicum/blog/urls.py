from django.urls import path

from . import views


app_name = 'blog'

urlpatterns = [
    path('',
         views.PostsListView.as_view(), name='index'),

    path('posts/<int:pk>/',
         views.PostsDetailView.as_view(), name='post_detail'),

    path('posts/create/',
         views.PostsCreateView.as_view(), name='create_post'),

    path('posts/<int:post_id>/edit/',
         views.PostsUpdateView.as_view(), name='edit_post'),

    path('posts/<int:post_id>/delete/',
         views.PostsDeleteView.as_view(), name='delete_post'),

    path('posts/<int:post_id>/comment/',
         views.CommentCreateView.as_view(), name='add_comment'),

    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),

    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),

    path('category/<slug:category_slug>/',
         views.CategoryListView.as_view(), name='category_posts'),

    path('profile/<str:username>/',
         views.UserDetailView.as_view(), name='profile'),

    path('profile/<str:username>/edit/',
         views.UserUpdateView.as_view(), name='edit_profile'),

    path('profile/<str:username>/edit/password/',
         views.UserPasswordUpdateView.as_view(), name='password_change'),
]
