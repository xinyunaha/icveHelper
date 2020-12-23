# Version 1.0
# Created by xinyunaha on 2020-12-21 15:21
import random

import requests
from io import BytesIO
from PIL import Image
import time

username = ''  # 用户名
password = ''  # 密码

minTime = 20  # 观看完一个小节的最小等待时间(单位：秒) 最低5,推荐20以上
maxTime = 40  # 观看完一个小节的最大等待时间(单位：秒) 推荐8,推荐30以上

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) '
                         'Chrome/86.0.4240.75 Safari/537.36'}


class Mooc:
    URL_LOGIN = 'https://mooc.icve.com.cn/portal/LoginMooc/loginSystem'
    URL_LOGIN_VERIFY = 'https://mooc.icve.com.cn/portal/LoginMooc/getVerifyCode'
    URL_USER_INFO = 'https://mooc.icve.com.cn/portal/LoginMooc/getUserInfo'
    URL_COURSE_ALL = 'https://mooc.icve.com.cn/portal/Course/getMyCourse'
    URL_LIST_MODULE = 'https://mooc.icve.com.cn/study/learn/getProcessList'
    URL_LIST_TOPIC = 'https://mooc.icve.com.cn/study/learn/getTopicByModuleId'
    URL_LIST_CELL = 'https://mooc.icve.com.cn/study/learn/getCellByTopicId'

    URL_STUDY_VIEW = 'https://mooc.icve.com.cn/study/learn/viewDirectory'
    URL_STUDY_PROCESS = 'https://mooc.icve.com.cn/study/learn/statStuProcessCellLogAndTimeLong'

    def __init__(self):
        self.session = requests.session()
        self.loginStatus = self.login()
        self.userid = self.getUserInfo()
        self.courseId = self.choseCourse()
        self.modelList = self.getModuleList()

    def Main(self):
        if type(self.loginStatus) == str:
            exit()
        self.Start()

    def login(self):
        if password == '' or password == '':
            print('请补全用户名及密码')
            exit(-1)
        codeContent = self.session.get(
            f'{Mooc.URL_LOGIN_VERIFY}?ts={round(time.time() * 1000)}',
            headers=headers).content
        byteIoObj = BytesIO()
        byteIoObj.write(codeContent)
        Image.open(byteIoObj).show()
        verifyCode = input('请输入验证码：')
        data = {
            'userName': username,
            'password': password,
            'verifycode': verifyCode
        }
        res = self.session.post(Mooc.URL_LOGIN, data=data, headers=headers).json()
        if res['code'] == 1:
            return True
        else:
            return res['msg']

    def getUserInfo(self):
        res = self.session.get(Mooc.URL_USER_INFO, headers=headers).json()
        try:
            print('欢迎您:', res['displayName'])
        except:
            print(res['msg'])
            exit(-1)
        return res['id']

    def choseCourse(self):
        data = {
            'isFinished': 0,
            'page': 1,
            'pageSize': 8
        }
        res = self.session.get(Mooc.URL_COURSE_ALL, data=data, headers=headers).json()
        print('=========================')
        for i in range(len(res['list'])):
            print(f'\t{i}、', res['list'][i].get('courseName'))
        while True:
            num = input('选择您的课程:')
            try:
                courseID = res['list'][int(num)].get('courseOpenId')
                break
            except:
                print('输入错误')
        return courseID

    def getModuleList(self):
        data = {
            'courseOpenId': self.courseId
        }
        res = self.session.post(Mooc.URL_LIST_MODULE, data=data,
                                headers=headers).json()
        return res['proces']['moduleList']

    def getTopicList(self, moduleID):
        data = {
            'courseOpenId': self.courseId,
            'moduleId': moduleID,
        }
        res = self.session.post(Mooc.URL_LIST_TOPIC, data=data,
                                headers=headers).json()
        return res['topicList']

    def getCellList(self, topicID):
        data = {
            'courseOpenId': self.courseId,
            'topicId': topicID
        }
        res = self.session.post(Mooc.URL_LIST_CELL, data=data, headers=headers).json()
        return res['cellList']

    def studyView(self, cellID, moduleID):
        data = {
            'courseOpenId': self.courseId,
            'cellId': cellID,
            'fromType': 'stu',
            'moduleId': moduleID,
        }
        res = self.session.post(Mooc.URL_STUDY_VIEW, data=data, headers=headers).json()
        return res['courseCell']

    def studyProcess(self, moduleID, cellID, _len, _time, _type):
        data = {
            'courseId': '',
            'courseOpenId': self.courseId,
            'moduleId': moduleID,
            'cellId': cellID,
            'auvideoLength': _len,
            'videoTimeTotalLong': _time,
            'sourceForm': _type
        }
        res = self.session.post(Mooc.URL_STUDY_PROCESS, data=data, headers=headers).json()
        return res['isStudy']

    def Start(self):
        for moduleItem in self.modelList:
            moduleID = moduleItem['id']
            moduleName = moduleItem['name']
            modulePercent = moduleItem['percent']
            print('当前单元:', moduleName)
            if modulePercent < 100:
                for topicItem in self.getTopicList(moduleID):
                    topicID = topicItem['id']
                    topicName = topicItem['name']
                    topicStatus = topicItem['studyStatus']
                    print('\t当前章节', topicName)
                    if topicStatus != 1:
                        for cellItem in self.getCellList(topicID):
                            for childItem in cellItem['childNodeList']:
                                cellID = childItem['Id']
                                cellName = childItem['cellName']
                                cellStatus = childItem['isStudyFinish']
                                cellType = childItem['cellType']
                                print(f'\t\t当前小节:{cellName}', end='')
                                if cellStatus:
                                    print('......已完成,跳过')
                                elif cellType == 5:
                                    print('......暂不支持自动答题,跳过')
                                    print(cellID,moduleID)
                                else:
                                    data = self.studyView(cellID, moduleID)
                                    _time = data['VideoTimeLong']
                                    _viewType = '888' if data['IsAllowDownLoad'] else '1229'
                                    process = self.studyProcess(moduleID, cellID, _time, _time, _viewType)
                                    _time = random.randint(minTime, maxTime)
                                    print(f'......成功 将在{_time}s后进行下一小节的观看' if process else '......失败')
                                    time.sleep(_time)
            pass


if __name__ == '__main__':
    Mooc().Main()
