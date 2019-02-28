from  django.conf.urls import  url
from  . import  views

urlpatterns = [
    url(r'^orders/(?P<order_id>\d+)/payment/$', views.Payment),
    url(r'^payment/status/$', views.PaymentStatus),
]
