from django.urls import path
from . import views

urlpatterns = [
    path('', views.business_list, name='business_list'),
    path('create/', views.business_create, name='business_create'),
    # Agar 'business_search' funksiyasi yo'q bo'lsa, uni olib tashlang yoki qo'shing
    # path('search/', views.business_search, name='business_search'),

    path('<int:pk>/', views.business_detail, name='business_detail'),
    path('<int:pk>/premium/', views.business_premium, name='business_premium'),

    # Like/Dislike uchun endpoint
    path('business/<int:pk>/like-toggle/', views.business_like_toggle, name='business_like_toggle'),
]
