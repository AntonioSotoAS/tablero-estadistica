from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('', include(('bases.urls', 'bases'), namespace="bases")),
    path('est/',include(('est.urls','est'),namespace='est')),
    path('admin/', admin.site.urls),
]