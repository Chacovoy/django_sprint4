from django.urls import path

from . import views as p_views


app_name = 'blog'

urlpatterns = [
    path('',
         p_views.PostsListView.as_view(), name='index'),

    path('posts/<int:pk>/',
         p_views.PostsDetailView.as_view(), name='post_detail'),

    path('posts/create/',
         p_views.PostsCreateView.as_view(), name='create_post'),

    path('posts/<int:post_id>/edit/',
         p_views.PostsUpdateView.as_view(), name='edit_post'),

    path('posts/<int:post_id>/delete/',
         p_views.PostsDeleteView.as_view(), name='delete_post'),

    path('posts/<int:post_id>/comment/',
         p_views.CommentCreateView.as_view(), name='add_comment'),

    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         p_views.CommentUpdateView.as_view(), name='edit_comment'),

    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         p_views.CommentDeleteView.as_view(), name='delete_comment'),

    path('category/<slug:category_slug>/',
         p_views.CategoryListView.as_view(), name='category_posts'),

    path('profile/<str:username>/',
         p_views.UserDetailView.as_view(), name='profile'),

    path('profile/<str:username>/edit/',
         p_views.UserUpdateView.as_view(), name='edit_profile'),

    path('profile/<str:username>/edit/password/',
         p_views.UserPasswordUpdateView.as_view(), name='password_change'),
]
