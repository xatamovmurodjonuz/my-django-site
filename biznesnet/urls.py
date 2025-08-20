from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import SignUpView

# Import main view for homepage
from businesses.views import business_list

urlpatterns = [
path('accounts/signup/', SignUpView.as_view(), name='signup'),

    path('admin/', admin.site.urls),

    path('businesses/', include('businesses.urls')),
    path('accounts/', include('django.contrib.auth.urls')),

    # ✅ Root URL -> business list view
    path('', business_list, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
