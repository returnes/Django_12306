__author__ = 'Caozy'

'''
12306-余票查询+订票
'''

import requests, re, time, ssl
from urllib import parse
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

import urllib3

urllib3.disable_warnings()  # 不显示警告信息
ssl._create_default_https_context = ssl._create_unverified_context
req = requests.Session()


class Leftquery(object):
    '''余票查询'''

    def __init__(self):
        self.station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js'
        self.headers = {
            'Host': 'kyfw.12306.cn',
            'If-Modified-Since': '0',
            'Pragma': 'no-cache',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

    def station_name(self, station):
        '''获取车站简拼'''
        html = requests.get(self.station_url, verify=False).text
        result = html.split('@')[1:]
        dict = {}
        for i in result:
            key = str(i.split('|')[1])
            value = str(i.split('|')[2])
            dict[key] = value
        return dict[station]

    def query(self, from_station, to_station, date):
        '''余票查询'''
        fromstation = self.station_name(from_station)
        tostation = self.station_name(to_station)
        url = 'https://kyfw.12306.cn/otn/leftTicket/queryX?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(date, fromstation, tostation)
        try:
            html = requests.get(url, headers=self.headers, verify=False).json()
            result = html['data']['result']
            if result == []:
                print('很抱歉,没有查到符合当前条件的列车!')
                exit()
            else:
                print(date + from_station + '-' + to_station + '查询成功!')

            return result
        except:
            print('查询信息有误!请重新输入!')
            exit()


class Login(object):
    '''登录模块'''

    def __init__(self, username, password):
        self.username = username
        self.password = password
        print(self.username,self.password)
        self.url_pic = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.15905700266966694'
        self.url_check = 'https://kyfw.12306.cn/passport/captcha/captcha-check'
        self.url_login = 'https://kyfw.12306.cn/passport/web/login'
        self.headers = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/login/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }

    def showimg(self):
        '''显示验证码图片'''
        global req
        html_pic = req.get(self.url_pic, headers=self.headers).content
        open('static/captcha/pic.jpg', 'wb').write(html_pic)
        img = mpimg.imread('static/captcha/pic.jpg')
        # plt.imshow(img)
        plt.axis('off')
        plt.show()

    def captcha(self, answer_num):
        '''填写验证码'''
        answer_sp = answer_num.split(',')
        answer_list = []
        an = {'1': (31, 35), '2': (116, 46), '3': (191, 24), '4': (243, 50), '5': (22, 114), '6': (117, 94),'7': (167, 120), '8': (251, 105)}
        for i in answer_sp:
            for j in an.keys():
                if i == j:
                    answer_list.append(an[j][0])
                    answer_list.append(',')
                    answer_list.append(an[j][1])
                    answer_list.append(',')
        s = ''
        for i in answer_list:
            s += str(i)
        answer = s[:-1]
        # 验证验证码
        form_check = {
            'answer': answer,
            'login_site': 'E',
            'rand': 'sjrand'
        }
        global req
        html_check = req.post(self.url_check, data=form_check, headers=self.headers).json()
        print(html_check)
        if html_check['result_code'] == '4':
            print('验证码校验成功!')
        else:
            print('验证码校验失败!')
            exit()

    def login(self):
        '''登录账号'''
        form_login = {
            'username': self.username,
            'password': self.password,
            'appid': 'otn'
        }
        print(self.username,self.password)
        global req
        html_login = req.post(self.url_login, data=form_login, headers=self.headers).json()
        print(html_login)
        if html_login['result_code'] == 0:
            print('恭喜您,登录成功!')
        else:
            print('账号密码错误,登录失败!')
            exit()


class Order(object):
    '''提交订单'''

    def __init__(self):
        self.url_uam = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
        self.url_uamclient = 'https://kyfw.12306.cn/otn/uamauthclient'
        self.url_order = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
        self.url_token = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
        self.url_pass = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
        self.url_confirm = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        self.url_checkorder = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
        self.url_count = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
        self.head_1 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }
        self.head_2 = {
            'Host': 'kyfw.12306.cn',
            'Referer': 'https://kyfw.12306.cn/otn/confirmPassenger/initDc',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
        }


    def auth(self):
        '''验证uamtk和uamauthclient'''
        # 验证uamtk
        form = {
            'appid': 'otn',
            # '_json_att':''
        }
        global req
        html_uam = req.post(self.url_uam, data=form, headers=self.head_1).json()
        print(html_uam)
        if html_uam['result_code'] == 0:
            print('恭喜您,uam验证成功!')
        else:
            print('uam验证失败!')
            exit()
        # 验证uamauthclient
        tk = html_uam['newapptk']

        form = {
            'tk': tk,
            # '_json_att':''
        }
        html_uamclient = req.post(self.url_uamclient, data=form, headers=self.head_1).json()
        print(html_uamclient)
        if html_uamclient['result_code'] == 0:
            print('恭喜您,uamclient验证成功!')
        else:
            print('uamclient验证失败!')
            exit()

    def order(self, result, train_number, from_station, to_station, date):
        '''提交订单'''
        # 用户选择要购买的车次的序号
        secretStr = parse.unquote(result[int(train_number) - 1].split('|')[0])
        back_train_date = time.strftime("%Y-%m-%d", time.localtime())
        form = {
            'secretStr': secretStr,  # 'secretStr':就是余票查询中你选的那班车次的result的那一大串余票信息的|前面的字符串再url解码
            'train_date': date,  # 出发日期(2018-04-08)
            'back_train_date': back_train_date,  # 查询日期
            'tour_flag': 'dc',  # 固定的
            'purpose_codes': 'ADULT',  # 成人票
            'query_from_station_name': from_station,  # 出发地
            'query_to_station_name': to_station,  # 目的地
            'undefined': ''  # 固定的
        }
        global req
        html_order = req.post(self.url_order, data=form, headers=self.head_1).json()
        # print(html_order)
        if html_order['status'] == True:
            print('恭喜您,提交订单成功!')
            return html_order
        else:
            print('提交订单失败!')
            exit()

    def price(self):
        '''打印票价信息'''
        form = {
            '_json_att': ''
        }
        global req
        html_token = req.post(self.url_token, data=form, headers=self.head_1).text
        token = re.findall(r"var globalRepeatSubmitToken = '(.*?)';", html_token)[0]
        leftTicket = re.findall(r"'leftTicketStr':'(.*?)',", html_token)[0]
        key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)',", html_token)[0]
        train_no = re.findall(r"'train_no':'(.*?)',", html_token)[0]
        stationTrainCode = re.findall(r"'station_train_code':'(.*?)',", html_token)[0]
        fromStationTelecode = re.findall(r"'from_station_telecode':'(.*?)',", html_token)[0]
        toStationTelecode = re.findall(r"'to_station_telecode':'(.*?)',", html_token)[0]
        date_temp = re.findall(r"'to_station_no':'.*?','train_date':'(.*?)',", html_token)[0]
        timeArray = time.strptime(date_temp, "%Y%m%d")
        timeStamp = int(time.mktime(timeArray))
        time_local = time.localtime(timeStamp)
        train_date_temp = time.strftime("%a %b %d %Y %H:%M:%S", time_local)
        train_date = train_date_temp + ' GMT+0800 (中国标准时间)'
        train_location = re.findall(r"tour_flag':'.*?','train_location':'(.*?)'", html_token)[0]
        purpose_codes = re.findall(r"'purpose_codes':'(.*?)',", html_token)[0]
        print('token值:' + token)
        print('leftTicket值:' + leftTicket)
        print('key_check_isChange值:' + key_check_isChange)
        print('train_no值:' + train_no)
        print('stationTrainCode值:' + stationTrainCode)
        print('fromStationTelecode值:' + fromStationTelecode)
        print('toStationTelecode值:' + toStationTelecode)
        print('train_date值:' + train_date)
        print('train_location值:' + train_location)
        print('purpose_codes值:' + purpose_codes)
        price_list = re.findall(r"'leftDetails':(.*?),'leftTicketStr", html_token)[0]
        # price = price_list[1:-1].replace('\'', '').split(',')
        print('票价:')
        for i in eval(price_list):
            # p = i.encode('latin-1').decode('unicode_escape')
            print(i + ' | ', end='')
        return train_date, train_no, stationTrainCode, fromStationTelecode, toStationTelecode, leftTicket, purpose_codes, train_location, token, key_check_isChange

    def passengers(self, token):
        '''打印乘客信息'''
        # 确认乘客信息
        form = {
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_pass = req.post(self.url_pass, data=form, headers=self.head_1).json()
        passengers = html_pass['data']['normal_passengers']
        print('\n')
        print('乘客信息列表:')
        for i in passengers:
            print(str(int(i['index_id']) + 1) + '号:' + i['passenger_name'] + ' | ', end='')
        print('\n')
        return passengers

    def chooseseat(self, passengers, passengers_name, choose_seat, token):
        '''选择乘客和座位'''
        seat_dict = {'无座': '1', '硬座': '1', '硬卧': '3', '软卧': '4', '高级软卧': '6', '动卧': 'F', '二等座': 'O', '一等座': 'M',
                     '商务座': '9'}
        choose_type = seat_dict[choose_seat]
        # pass_num = len(passengers_name.split(','))  # 购买的乘客数
        # pass_list = passengers_name.split(',')
        pass_num=len(passengers_name)
        pass_list=passengers_name
        pass_dict = []
        for i in pass_list:
            info = passengers[int(i) - 1]
            pass_name = info['passenger_name']  # 名字
            pass_id = info['passenger_id_no']  # 身份证号
            pass_phone = info['mobile_no']  # 手机号码
            pass_type = info['passenger_type']  # 证件类型
            dict = {
                'choose_type': choose_type,
                'pass_name': pass_name,
                'pass_id': pass_id,
                'pass_phone': pass_phone,
                'pass_type': pass_type
            }
            pass_dict.append(dict)

        num = 0
        TicketStr_list = []
        for i in pass_dict:
            if pass_num == 1:
                TicketStr = i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ',N'
                TicketStr_list.append(TicketStr)
            elif num == 0:
                TicketStr = i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ','
                TicketStr_list.append(TicketStr)
            elif num == pass_num - 1:
                TicketStr = 'N_' + i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ',N'
                TicketStr_list.append(TicketStr)
            else:
                TicketStr = 'N_' + i['choose_type'] + ',0,1,' + i['pass_name'] + ',' + i['pass_type'] + ',' + i[
                    'pass_id'] + ',' + i['pass_phone'] + ','
                TicketStr_list.append(TicketStr)
            num += 1

        passengerTicketStr = ''.join(TicketStr_list)
        print(passengerTicketStr)

        num = 0
        passengrStr_list = []
        for i in pass_dict:
            if pass_num == 1:
                passengerStr = i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ',1_'
                passengrStr_list.append(passengerStr)
            elif num == 0:
                passengerStr = i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ','
                passengrStr_list.append(passengerStr)
            elif num == pass_num - 1:
                passengerStr = '1_' + i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ',1_'
                passengrStr_list.append(passengerStr)
            else:
                passengerStr = '1_' + i['pass_name'] + ',' + i['pass_type'] + ',' + i['pass_id'] + ','
                passengrStr_list.append(passengerStr)
            num += 1

        oldpassengerStr = ''.join(passengrStr_list)
        print(oldpassengerStr)
        form = {
            'cancel_flag': '2',
            'bed_level_order_num': '000000000000000000000000000000',
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldpassengerStr,
            'tour_flag': 'dc',
            'randCode': '',
            'whatsSelect': '1',
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_checkorder = req.post(self.url_checkorder, data=form, headers=self.head_2).json()
        print(html_checkorder)
        if html_checkorder['status'] == True:
            print('检查订单信息成功!')
        else:
            print('检查订单信息失败!')
            exit()

        return passengerTicketStr, oldpassengerStr, choose_type

    def leftticket(self, train_date, train_no, stationTrainCode, choose_type, fromStationTelecode, toStationTelecode,
                   leftTicket, purpose_codes, train_location, token):
        '''查看余票数量'''
        form = {
            'train_date': train_date,
            'train_no': train_no,
            'stationTrainCode': stationTrainCode,
            'seatType': choose_type,
            'fromStationTelecode': fromStationTelecode,
            'toStationTelecode': toStationTelecode,
            'leftTicket': leftTicket,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_count = req.post(self.url_count, data=form, headers=self.head_2).json()
        print(html_count)
        if html_count['status'] == True:
            print('查看余票数量成功!')
            count = html_count['data']['ticket']
            print('此座位类型还有余票' + count + '张~')
            return count
        else:
            print('查看余票数量失败!')
            exit()

    def sure(self,tag):
        '''是否确认购票'''
        # 用户是否继续购票:
        i = tag
        # i = input('是否确定购票?(Y or N):')
        if i == 'Y' or i == 'y':
            pass
        else:
            print('测试流程，关闭外部接口提交。。。。。。')
            exit()

    def confirm(self, passengerTicketStr, oldpassengerStr, key_check_isChange, leftTicket, purpose_codes,
                train_location, token):
        '''最终确认订单'''
        form = {
            'passengerTicketStr': passengerTicketStr,
            'oldPassengerStr': oldpassengerStr,
            'randCode': '',
            'key_check_isChange': key_check_isChange,
            'choose_seats': '',
            'seatDetailType': '000',
            'leftTicketStr': leftTicket,
            'purpose_codes': purpose_codes,
            'train_location': train_location,
            '_json_att': '',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',
            'REPEAT_SUBMIT_TOKEN': token
        }
        global req
        html_confirm = req.post(self.url_confirm, data=form, headers=self.head_2).json()
        print(html_confirm)
        if html_confirm['status'] == True:
            print('确认购票成功!')
            return True
        else:
            print('确认购票失败!')
            exit()