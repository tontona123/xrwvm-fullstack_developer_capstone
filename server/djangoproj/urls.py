# server/djangoproj/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('djangoapp/', include('djangoapp.urls')),  # เปลี่ยน 'djangoapp' ให้เป็นชื่อแอปของคุณตามที่ใช้งานจริง
    path('', TemplateView.as_view(template_name="Home.html")),
    path('about/', TemplateView.as_view(template_name="About.html")),
    path('login/', TemplateView.as_view(template_name="index.html")),
    path('contact/', TemplateView.as_view(template_name="Contact.html")),
    path('register/', TemplateView.as_view(template_name="index.html")),
    path('dealers/', TemplateView.as_view(template_name="index.html")),
    path('dealer/<int:dealer_id>/', TemplateView.as_view(template_name="index.html")),  # เพิ่ม '/' หลัง dealer_id
    path('postreview/<int:dealer_id>',TemplateView.as_view(template_name="index.html")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
