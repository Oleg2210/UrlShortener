from django.urls import path, re_path
from . import views

app_name = 'api'

urlpatterns = [
    re_path(r'^$', views.AvailableLinksView.as_view()),
    re_path(r'^api/?$', views.AvailableLinksView.as_view()),
    re_path(r'^api/shorten/?$', views.CreateView.as_view()),
    re_path(r'^api/shortened_links/?([1-9][0-9]*)?$', views.ListView.as_view()),
    re_path(r'^([0-9a-zA-Z]{1,8})$', views.redirect),
]
