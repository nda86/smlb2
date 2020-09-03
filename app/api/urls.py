from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from api import views

urlpatterns = [
    url(r'^auth-token/$', views.login),
    url(r'^goods/$', views.Goods.as_view()),
    url(r'^reports/$', views.Reports.as_view()),
    url(r'^sync/$', views.Sync.as_view()),
    url(r'^admin/$', admin.sites.AdminSite),
]