from  datetime import  datetime
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render,redirect
from df_cart.models import CartInfo
from df_goods.models import GoodsInfo
from df_order.models import OrderDetailInfo, OrderInfo
from  df_user import  user_decorator
from df_user.models import UserInfo
from django.db import  transaction

@user_decorator.login
def order(request):
    """
    此函数用户给下订单页面展示数据
    接收购物车页面GET方法发过来的购物车中物品的id，构造购物车对象供订单使用
    """
    uid = request.session.get('user_id')
    user = UserInfo.objects.get(id=uid)

    # 获取勾选的每一个订单对象，构造成list，作为上下文传入下单页面
    orderid = request.GET.getlist('orderid')
    orderlist = []

    for id in orderid:
        orderlist.append(CartInfo.objects.get(id=int(id)))

    # 判断用户手机号是否为空，分别做展示
    if user.uphone == '':
        uphone = ''
    else:
        uphone = user.uphone[0:4] + \
            '****' + user.uphone[-4:]

    # 构造上下文
    context = {'title': '提交订单', 'page_name': 1, 'orderlist': orderlist,
               'user': user, 'ureceive_phone': uphone}

    return render(request, 'df_order/place_order.html', context)


@transaction.atomic()
@user_decorator.login
def order_handle(request):
    #保存一个事物点
    tran_id = transaction.savepoint()
    #接收购物车编号
    # 根据POST和session获取信息
    # cart_ids=post.get('cart_ids')
    try:
        post = request.POST
        orderlist = post.getlist('id[]')
        total = post.get('total')
        address = post.get('address')

        order=OrderInfo()
        now=datetime.now()
        uid = request.session.get('user_id')
        order.oid='%s%d'%(now.strftime('%Y%m%d%H%M%S'),uid)
        order.user_id=uid
        order.odate=now
        order.ototal=Decimal(total)
        order.oaddress = address
        order.save()

        # 遍历购物车中提交信息，创建订单详情表
        for orderid in orderlist:
            cartinfo = CartInfo.objects.get(id=orderid)
            # good = GoodsInfo.objects.get(cartinfo__id=cartinfo.id)
            good = GoodsInfo.objects.get(pk=cartinfo.goods_id)
            # print '*'*10
            # print cartinfo.goods_id
            # 判断库存是否够
            if int(good.gkucun) >= int(cartinfo.count):
                # 库存够，移除购买数量并保存
                good.gkucun -= int(cartinfo.count)
                good.save()

                goodinfo = GoodsInfo.objects.get(cartinfo__id=orderid)

                # 创建订单详情表
                detailinfo = OrderDetailInfo()
                detailinfo.goods_id = int(goodinfo.id)
                detailinfo.order_id = int(order.oid)
                detailinfo.price = Decimal(int(goodinfo.gprice))
                detailinfo.count = int(cartinfo.count)
                detailinfo.save()

                # 循环删除购物车对象
                cartinfo.delete()
            else:
                # 库存不够出发事务回滚
                transaction.savepoint_rollback(tran_id)
                # 返回json供前台提示失败
                return JsonResponse({'status': 2})
    except Exception as e:
            print('==================%s'%e)
            transaction.savepoint_rollback(tran_id)
        # 返回json供前台提示成功
    return JsonResponse({'status': 1})


# @transaction.atomic()
def pay(request,oid):
    tran_id = transaction.savepoint()
    # try:
    order = OrderInfo.objects.get(oid=oid)
    order.zhifu = 1

    order.save()
    # except Exception as e:
    # print '==================%s' % e
    # transaction.savepoint_rollback(tran_id)
    context = {'oid': oid}
    return render(request, 'df_order/pay.html', context)