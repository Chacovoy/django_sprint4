from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Подключаем маршруты для работы с пользователями из django.contrib.auth.urls
urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    # Без этой строчки не проходит автотесты
    path('auth/', include('blogicum.auth')),
    path('auth/', include('django.contrib.auth.urls')),
]

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
