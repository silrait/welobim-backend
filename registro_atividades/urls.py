from rest_framework import routers
from registro_atividades import views
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'users', views.CompanyUserViewSet)
router.register(r'companies', views.CompanyViewSet)
router.register(r'logs', views.LogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]