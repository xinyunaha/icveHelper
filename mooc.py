from io import BytesIO
from PIL import Image
import time
import random
import json
import sys
import math
import requests

# version 1.0
# author: xinyunaha
# date: 2020.11.10 09:52
# * 写了www.icve.com.cn适用的，结果老师说得用mooc.icve.com.cn ~~强颜欢笑 淦!~~

username = ''  # 用户名
password = ''  # 密码
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) '
                         'Chrome/86.0.4240.75 Safari/537.36'}


class Mooc:
    def __init__(self):
        self.verifyCode = None
        self.userid = None
        self.courseId = None
        self.cellId = None
        self.notWatched = {}
        self.session = requests.session()
        self.username = username
        self.password = password
        self.verify()
        self.login()
        self.getUserInfo()
        self.getAllClass()
        # self.getWatchTime()
        # self.Run()

    def verify(self):
        codeContent = self.session.get(
            f'https://mooc.icve.com.cn/portal/LoginMooc/getVerifyCode?ts={round(time.time() * 1000)}',
            headers=headers).content
        byteIoObj = BytesIO()
        byteIoObj.write(codeContent)
        Image.open(byteIoObj).show()
        self.verifyCode = input('请输入验证码：')

    def login(self):
        data = {'userName': self.username,
                'password': self.password,
                'verifycode': self.verifyCode}
        res = self.session.post('https://mooc.icve.com.cn/portal/LoginMooc/loginSystem', headers=headers,
                                data=data).text
        _json = json.loads(res)
        if _json['code'] == 1:
            print('登录成功')
        else:
            print(_json['msg'])
            sys.exit(-1)

    def getUserInfo(self):
        res = self.session.get('https://mooc.icve.com.cn/portal/LoginMooc/getUserInfo', headers=headers).text
        _json = json.loads(res)
        self.userid = _json['id']
        print('欢迎您:', self.userid)

    def getAllClass(self):
        data = {'isFinished': 0, 'page': 1, 'pageSize': 8}
        res = self.session.get("https://mooc.icve.com.cn/portal/Course/getMyCourse", headers=headers,
                               data=data).text
        print('=========================')
        for i in range(len(json.loads(res)['list'])):
            print(f'\t{i}、', json.loads(res)['list'][i].get('courseName'))
        while True:
            num = input('选择您的课程:')
            try:
                self.courseId = json.loads(res)['list'][int(num)].get('id')
                break
            except:
                print('输入错误')

    def Run(self):
        pass


if __name__ == "__main__":
    Mooc()
