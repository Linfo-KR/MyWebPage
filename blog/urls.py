from django.urls import path
from . import views


urlpatterns = [
    path('', views.PostList.as_view()),
    path('<int:pk>/', views.PostDetail.as_view()),
    path('category/<str:slug>/', views.category_page)
    
    # With FBV
    # path('', views.index),
    
    # With FBV
    # path('<int:pk>', views.single_post_page),
]