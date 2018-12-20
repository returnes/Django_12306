from django.shortcuts import render
from django.views.generic.base import View
from django.http import HttpResponse
import json
import time

from spiders.spider import select, Login, Order, Leftquery

query = Leftquery()
order = Order()
content = []
result = []


# train_info=train_info


# Create your views here.


class LoginView(View):
    def get(self, request):
        login = Login('', '')  # 链接请求，初始化登录类传入空用户密码
        login.showimg()  # 获取验证码图片
        return render(request, 'login.html', {'url': '/static/captcha/pic.jpg'})

    def post(self, request):
        # global username, password
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        answer_num = request.POST.getlist('check')
        answer_num = ','.join(answer_num)
        print(answer_num)
        login = Login(username, password)
        # login.showimg()
        login.captcha(answer_num)  # 填写验证码并验证
        login.login()

        # order = Order()
        # order.auth()

        return render(request, 'query.html', {'username': username, 'password': password})


class OrderView(View):
    def get(self, request):
        pass

    def post(self, request):
        global order
        from_station = request.POST.get('fromstation', '')
        to_station = request.POST.get('tostation', '')
        date = request.POST.get('date', '')
        trainnum = request.POST.get('trainnum', '')
        nums = request.POST.getlist('num', '')
        # 用户选择要购买的车次的序号
        # train_number = input('请输入您要购买的车次的序号(例如:6):')
        # 提交订单
        # nums=nums.split(',')
        global query
        global result
        global content
        train_list = []
        for num in nums:
            result = query.query(from_station, to_station, date)
            order.order(result, num, from_station, to_station, date)
            # 检查订单

            info = result[int(num) - 1].split('|')
            train_dict = {'checi': info[3], 'begin_time': info[8], 'end_time': info[9], 'lishi': info[10],
                          'gjrw': info[21], 'ruanwo': info[23], 'wuzuo': info[26], 'yingwo': info[28],
                          'yingzuo': info[29], 'erdengzuo': info[30], 'yidengzuo': info[31],
                          'shangwuzuo': info[32], 'dongwo': info[33], 'num': num}
            train_list.append(train_dict)

        content = order.price()  # 打印出票价信息
        passengers = order.passengers(content[8])  # 打印乘客信息
        return render(request, 'order.html', {
            'from_station': from_station,
            'to_station': to_station,
            'date': date,
            'content': content,
            'passengers': passengers,
            'trainnum': trainnum,
            'nums': nums,
            'train_list': train_list,
        })


class ConfirmView(View):
    def get(self, request):
        if info[0] != '' and info[0] != 'null':
            if info[index] == '无' and info[index] == '':
                return HttpResponse(
                    json.dumps({"train": info[3], "seat": seat, "count": info[index]}),
                    content_type='application/json')
            else:
                return HttpResponse(
                    json.dumps({"train": info[3], "seat": seat, "count":info[index]}),
                    content_type='application/json')


    def post(self, request):
        fromstation = request.POST.get('fromstation', '')
        tostation = request.POST.get('tostation', '')
        date = request.POST.get('date', '')
        nums = request.POST.getlist('num', '')
        trainnum = request.POST.get('trainnum', '')
        global seat
        seat = request.POST.get('seat', '')
        passengers_name = request.POST.getlist('passengers', '')
        print("起始车站：%s\n终点车站：%s\n日期：%s\n车次号：%s\n席位：%s\n乘客：%s" % (
            fromstation, tostation, date, nums, seat, passengers_name))

        global result
        seater = {'高级软卧': 21, '软卧': 23, '无座': 26, '硬卧': 28, '硬座': 29, '二等座': 30, '一等座': 31, '商务座': 32, '动卧': 33}
        global index
        index = int(seater[seat])
        while True:
            for num in nums:
                global info
                info = result[int(num) - 1].split('|')
                if info[0] != '' and info[0] != 'null':

                    if info[index] != '无' and info[index] != '':
                        global order
                        # content = order.price()  # 打印出票价信息
                        global content
                        passengers = order.passengers(content[8])  # 打印乘客信息
                        pass_info = order.chooseseat(passengers, passengers_name, seat, content[8])
                        # 查看余票数
                        order.leftticket(content[0], content[1], content[2], pass_info[2], content[3], content[4],
                                         content[5], content[6], content[7], content[8])
                        # 是否确认购票,购票开关
                        order.sure('y')
                        # 最终确认订单
                        result = order.confirm(pass_info[0], pass_info[1], content[9], content[5], content[6],
                                               content[7], content[8])
                        # return render(request, 'order.html')
                        if result:
                            return HttpResponse(json.dumps({"status": "success",
                                                            "msg": "起始车站：%s\n终点车站：%s\n日期：%s\n车次号：%s\n席位：%s\n乘客：%s" % (
                                                                fromstation, tostation, date, info[3], seat,
                                                                passengers)}),
                                                content_type='application/json')
                            # return HttpResponse('{"status":"success"}', content_type='application/json')
                        else:
                            return HttpResponse(json.dumps({"status": "fail", "msg": "遇到错误，停止刷票"}),
                                                content_type='application/json')
                    elif info[index] == '无' or info[index] == '':
                        time.sleep(1)
                        print('该席位暂时无票，正在刷新。。。。。。。')
                        # 在此调用get方法存储刷票次数及动态信息
                        # global train_info
                        result = query.query(fromstation, tostation, date)
                        # from django.contrib import messages
                        # messages.add_message(request, messages.ERROR, 'wupiao')
                        # global train_info
                        # train_info=result
                        # HttpResponse(json.dumps({"status": "fail", "msg": "z终止"}), content_type='application/json')
                        continue


class QueryView(View):
    def get(self, request):
        return render(request, 'query.html')

    def post(self, request):
        # order = Order()
        global order
        order.auth()
        # 接收 起始站、终点站、日期
        from_station = request.POST.get('fromstation', '')
        to_station = request.POST.get('tostation', '')
        date = request.POST.get('date', '')
        # 余票查询
        global query
        result = query.query(from_station, to_station, date)
        # print(result)
        # 打印出所有车次信息
        num = 1  # 用于给车次编号,方便选择要购买的车次
        trains_list = [from_station, to_station, date]
        # for i in result:
        # info = i.split('|')
        while num <= len(result):
            info = result[int(num) - 1].split('|')
            if info[0] != '' and info[0] != 'null':
                # print(str(num) + '.' + info[3] + '车次还有余票:')
                # print('出发时间:' + info[8] + ' 到达时间:' + info[9] + ' 历时多久:' + info[10] + ' ', end='')
                # seat = {21: '高级软卧', 23: '软卧', 26: '无座', 28: '硬卧', 29: '硬座', 30: '二等座', 31: '一等座', 32: '商务座', 33: '动卧'}
                shangwuzuo = info[32]
                if info[25] != '无' and info[25] != '':
                    shangwuzuo = info[25]

                train_dict = {'checi': info[3], 'begin_time': info[8], 'end_time': info[9], 'lishi': info[10],
                              'gjrw': info[21], 'ruanwo': info[23], 'wuzuo': info[26], 'yingwo': info[28],
                              'yingzuo': info[29], 'erdengzuo': info[30], 'yidengzuo': info[31],
                              'shangwuzuo': shangwuzuo, 'dongwo': info[33], 'num': num}
                trains_list.append(train_dict)
                num += 1
            else:
                num += 1
                continue

        # data={
        #     "trains_info": trains_list,
        #     'from_station': from_station,
        #     'to_station': to_station,
        #     'date': date,
        # }
        # print(json.dumps(trains_list))

        return HttpResponse(json.dumps(trains_list), content_type='application/json')
        # return HttpResponse('{"status":"success"}', content_type='application/json')
