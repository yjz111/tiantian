from django.db import models
# Create your models here.
from df_order.models import OrderInfo


class Payment(models.Model):
    #支付信息
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE)
    trade_id = models.CharField(max_length=100, unique=True, null=True, blank=True)


