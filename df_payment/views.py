import os

import alipay
from django.http import JsonResponse
from django.shortcuts import render
from df_order.models import  OrderInfo
from tiantian import settings
from  .models import  Payment
from  alipay import AliPay

# Create your views here.

def PaymentStatus(request):
    pass
    data = request.GET.dict()
    signature = data.pop('sign')

    # 创建AliPay实例对象
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,  # 开发者应用APPID
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "../df_order/keys/app_private_key.pem"),
        alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            "../df_order/keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=settings.ALIPAY_DEBUG  # 默认False，是否使用的是沙箱环境
    )

    success = alipay.verify(data, signature)

    if not success:
        return JsonResponse({'message': '非法请求'}, status=404)

    # 2. 校验订单是否有效
    order_id = request.query_params.get('out_trade_no')
    try:
        order = OrderInfo.objects.get(
            order_id=order_id,
            user=request.user,
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'],  # 待支付
            pay_method=OrderInfo.PAY_METHODS_ENUM['ALIPAY'],  # 支付宝支付方式
        )
    except OrderInfo.DoesNotExist:
        return JsonResponse({'message': '无效的订单信息'}, status=404)

    # 3. 保存订单支付结果，更新订单支付状态
    trade_id = request.query_params.get('trade_no')

    Payment.objects.create(
        order=order,
        trade_id=trade_id
    )

    # 更新订单支付状态
    order.status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']  # 2
    order.save()

    # 4. 返回应答
    return JsonResponse({'trade_id': trade_id})



def Payment(request):
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,  # 开发者应用APPID
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "../df_order/keys/app_private_key.pem"),
        alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            "../df_order/keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=settings.ALIPAY_DEBUG  # 默认False，是否使用的是沙箱环境
    )

    # 组织支付参数
    # 电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=OrderInfo.oid,  # 商户订单号
        total_amount=str(OrderInfo.ototal),  # 支付总金额 Decimal
        subject='天天%s' % OrderInfo.oid,
        return_url="http://www.baidu.com",  # 用户支付成功之后回调地址
        notify_url=None  # 可选, 不填则使用默认notify url
    )

    # 3. 返回支付宝支付地址
    pay_url = settings.ALIPAY_URL + '?' + order_string
    return JsonResponse({'alipay_url': pay_url})

