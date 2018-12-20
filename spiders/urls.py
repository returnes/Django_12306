# Author Caozy

from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from .views import LoginView,OrderView,QueryView,ConfirmView

urlpatterns = [
    # path('admin/', admin.site.urls),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^order/$', OrderView.as_view(), name='order'),
    url(r'^query/$', QueryView.as_view(), name='query'),
    url(r'^confirm/$', ConfirmView.as_view(), name='confirm'),
]
app_name='spiders'

