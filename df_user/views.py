from django.shortcuts import render
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse

from df_order.models import OrderInfo
from . import  user_decorator
from df_goods.models import GoodsInfo
from .models import *
from hashlib import sha1
from django.http import JsonResponse
from  .islogin import islogin
from django.core.paginator import Paginator
from df_cart.models import *


# Create your views here.
def register(request):
    return render(request,'df_user/register.html')

#登录处理
def register_handle(requst):
    response = HttpResponse()
    # 接收用户输入
    post = requst.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    ucpwd = post.get('cpwd')
    uemail = post.get('email')

    if upwd != ucpwd:
        return redirect('/user/register/')
    s1 = sha1()
    s1.update(upwd.encode('utf-8'))
    upwd3 = s1.hexdigest()

    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()

    return redirect('/user/login/')


def register_exist(request):    #判断用户名是否已经存在
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()    #count为0或1
    return JsonResponse({'count':count})


def login(request):
    uname = request.COOKIES.get('uname','')     #获取cookie
    context = {'title':'用户登录', 'error_name':0, 'error_pwd':0, 'uname': uname}
    return render(request, 'df_user/login.html', context)


def login_handle(request):
    #接受请求信息
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu=post.get('jizhu', 0)      #当jizhu有值时,即jizhu被勾选等于1时,返回的数据为1,否则get返回后面的0

    #根据用户名查询对象
    users = UserInfo.objects.filter(uname=uname)  #查询结果为一个列表

    #判断：如果未查到则说明用户名错误，如果查到则判断密码是否正确，如果密码正确，则返回用户中心
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd.encode("utf-8"))
        if s1.hexdigest() == users[0].upwd:
            url = request.COOKIES.get('url','/')    #获取登录之前进入的页面,如果没有,则进入首页
            red = HttpResponseRedirect(url)   #用变量记住,方便设置cookie
            #记住用户名
            if jizhu != 0:
                red.set_cookie('uname',uname)       #设置cookie保存用户名
            else:
                red.set_cookie('uname','', max_age=-1)  #max_age指的是过期时间,当为-1时为立刻过期
            request.session['user_id'] = users[0].id    #把用户id和名字放入session中
            request.session['user_name'] = uname
            return red
        else:
            context = {'title':'用户登录', 'error_name':0, 'error_pwd':1, 'uname':uname, 'upwd':upwd}
            return render(request, 'df_user/login.html', context)
    context = {'title': '用户登录', 'error_name': 1, 'error_pwd': 0, 'uname': uname, 'upwd': upwd}
    return render(request, 'df_user/login.html', context)


def logout(request):
    del request.session['user_id']
    del request.session['user_name']
    return redirect('/')


def info(request):
    user_email = UserInfo.objects.get(id=request.session['user_id']).uemail

    #最近浏览
    goods_ids = request.COOKIES.get('goods_ids', '')
    goods_id_list = goods_ids.split(',')
    goods_list=[]
    if len(goods_ids):
        for goods_id in goods_id_list:
            goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))

    context = {'title': '用户中心',
               'user_email': user_email,
               'user_name': request.session['user_name'],
               'page_name':1,'info':1,
               'goods_list':goods_list}
    return render(request, 'df_user/user_center_info.html', context)

@user_decorator.login
def order(request):     #全部订单
    context = {'title': '用户中心'}
    return render(request, 'df_user/user_center_order.html', context)


@user_decorator.login
def site(request):      #收货地址
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method == 'POST':
        post = request.POST
        user.ushou = post.get('ushou')
        user.uaddress = post.get('uaddress')
        user.uyoubian = post.get('uyoubian')
        user.uphone = post.get('uphone')
        if not(user.ushou and user.uaddress and user.uaddress and user.uphone):
            return redirect('/user/site/')
    context = {'title': '用户中心', 'user': user}
    user.save()
    return render(request, 'df_user/user_center_site.html', context)

@user_decorator.login
def user_center_order(request, pageid):
    """
    此页面用户展示用户提交的订单，由购物车页面下单后转调过来，也可以从个人信息页面查看
    根据用户订单是否支付、下单顺序进行排序
    """

    uid = request.session.get('user_id')
    # 订单信息，根据是否支付、下单顺序进行排序
    orderinfos = OrderInfo.objects.filter(
        user_id=uid).order_by('zhifu', '-oid')

    # 分页
    #获取orderinfos list  以两个为一页的 list
    paginator = Paginator(orderinfos, 2)
    # 获取 上面集合的第 pageid 个 值
    orderlist = paginator.page(int(pageid))
    #获取一共多少 页
    plist = paginator.page_range
    #3页分页显示
    qian1 = 0
    hou = 0
    hou2 = 0
    qian2 = 0
    # dd = dangqian ye
    dd = int(pageid)
    lenn = len(plist)
    if dd>1:
        qian1 = dd-1
    if dd>=3:
        qian2 = dd-2
    if dd<lenn:
        hou = dd+1
    if dd+2<=lenn:
        hou2 = dd+2



    # 构造上下文
    context = {'page_name': 1, 'title': '全部订单', 'pageid': int(pageid),
               'order': 1, 'orderlist': orderlist, 'plist': plist,
               'pre':qian1,'next':hou,'pree':qian2,'lenn':lenn,'nextt':hou2}

    return render(request, 'df_user/user_center_order.html', context)