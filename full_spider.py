# # coding:utf-8
#
# TIMEOUT = 10
# from requests import Request
#
#
# class WeixinRequest(Request):
#     def __init__(self,url,callback,method='GET',headers=None,need_proxy=False,fail_time=0,timeout=TIMEOUT):
#         Request.__init__(self,method,url,headers)
#         self.callback = callback
#         self.need_proxy = need_proxy
#         self.fail_time = fail_time
#         self.timeout = timeout
#
# from pickle import dumps,loads
# from requests import WeixinRequest
# from redis import StrictRedis
#
#
# class RedisQueue():
#     def __init__(self):
#         """
#         初始化Redis
#         """
#         self.db = StrickRedis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD)
#
#     def add(self,request):
#         """
#         向队列添加序列化后的Request
#         :param request: 请求对象
#         :return: 添加结果
#         """
#         if isinstance(request，WeixinRequest):
#             return self.db.rpush(REDIS_KEY,dumps(request))
#         return False
#
#     def pop(self):
#         """
#         取出下一个Request并反序列化
#         :return: Request or None
#         """
#         if self.db.llen(REDIS_KEY):
#             return loads(self.db.lpop(REDIS_KEY))
#         else:
#             return False
#
#     def is_empty(self):
#         """
#         判断队列是否为空
#         :return:
#         """
#         return self.db.llen(REDIS_KEY) == 0
#
#
# from requests import Session
# from db import RedisQueue
# from request import WeinxinRequest
# from urllib.parse import urlencode
# from requests import ReadTimeout,ConnectionError
# from pyquery import PyQuery as pq
# from config import *
# from db import RedisQueue
# from mysql import MySQL
# import requests
#
# # 构造爬虫类
# class Spider():
#     base_url = 'http://weixin.sogou.com/weixin'
#     keyword = 'NBA'
#     headers = {
#         'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#         'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
#         'Cache-Control':'max-age=0',
#         'Connection':'keep-alive',
#         'Cookie':'CXID=169CA3DD499C81E8176DB584E349003D; ad=sZllllllll2b@7ydlllllVsMeR1lllll1ezLhyllll'
#                  '9lllll4Vxlw@@@@@@@@@@@; SUID=C9B616D33765860A5BFEC43D0001EDD6; ABTEST=2|1544848057|v1; '
#                  'IPLOC=CN1100; weixinIndexVisited=1; SUV=00941C7C6FC103C85C1482BADA674534; sct=1; JSES'
#                  'SIONID=aaaeKqBBMfZ-IfVK7S6Cw; PHPSESSID=q0nm7ffc1t2472it2tu8r63cn7; SUIR=955E9F325D582'
#                  '359A7644C655EE62356; SNUID=E822E14E21255D26DEAADAE621E759F4; ppinf=5|1544852927|154606'
#                  '2527|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTozOiU3RXxjcnQ6MTA6MTU0NDg1MjkyN3xyZ'
#                  'WZuaWNrOjM6JTdFfHVzZXJpZDo0NDpvOXQybHVOWnAtQjVSVXFEWFFEY1JvLWg4UTJZQHdlaXhpbi5zb2h1LmN'
#                  'vbXw; pprdig=MZsdme_nYk1gkh8vE02DpuMnlxkZl6d_6rtoJ90Sl_zqQ0TFbPBUV8oGm5WjAsjNKE43_Bg4V'
#                  'ZmiEo0QRYK63_7XN0SGFfuygWR3iplLDX98Ff6uGAfDE7sBPGo_qGKS68tBzS27ynMqNw_BwsEHGjDP4lmSqM3u'
#                  'qyq32aCSdeY; sgid=12-38368811-AVwUlb8QqJ39TMyubtn53K8; ppmdig=154485292700000064bb3d155'
#                  'b87189598fbc21a631552d9',
#         'Host':'weixin.sogou.com',
#         'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko)'
#                      ' Chrome/71.0.3578.80 Safari/537.36',
#     }
#     session = Session()
#     queue = RedisQueue()
#     mysql = MySQL()
#
#
#     def get_proxy(self):
#         """
#         从代理池获得代理
#         :return:
#         """
#         try:
#             response = requests.get(PROXY_POOL_URL)
#             if response.status_code == 200:
#                 print('Get Proxy',response.text)
#                 return response.text
#             return None
#         except requests.ConnectionError:
#             return None
#
#     def start(self):
#         """
#         初始化工作
#         :return:
#         """
#         # 全局更新Headers
#         self.session.headers.update(self.headers)
#         start_url = self.base_url + '?' + urlencode({'query':self.keyword,'type':2})
#         weixin_request = WeinxinRequest(url=start_url,callback=self.parse_index,need_proxy=True)
#         # 调度第一个请求
#         self.queue.add(weixin_request)
#
#
#     VALID_STATUSES = [200]
#
#     def schedule(self):
#         """
#         调度请求
#         :return:
#         """
#         while not self.queue.is_empty():
#             weixin_request = self.queue.pop()
#             callback = weixin_request.callback
#             print('Schedule',weixin_request.url)
#             response = self.request(weixin_request)
#             if response and response.status_code in VALID_STATUSES:
#                 results = list(callback(response))
#                 if results:
#                     for result in results:
#                         print('New Result',result)
#                         if isinstance(result,WeinxinRequest):
#                             self.queue.add(result)
#                         if isinstance(result,dict):
#                             self.mysql.insert('articles',result)
#                 else:
#                     self.error(weixin_request)
#             else:
#                 self.error(weixin_request)
#
#
#
#
#     def request(self,weixin_request):
#         """
#         执行请求
#         :param weixin_request: 请求
#         :return: 响应
#         """
#         try:
#             if weixin_request.need_proxy:
#                 proxy = get_proxy()
#                 if proxy:
#                     proxies = {
#                         'http':'http://' + proxy,
#                         'https':'https://' + proxy
#                     }
#                     return self.session.send(weixin_request.prepare(),
#                                              timeout=weixin_request.timeout,allow_redirects=False,proxies=proxies)
#             return self.session.send(weixin_request.prepare(),timeout=weixin_request.timeout,allow_redirects=False)
#         except (ConnectionError,ReadTimeout) as e:
#             print(e.args)
#             return False
#
#
#
#     def parse_index(self,response):
#         """
#         解析索引页
#         :param response: 响应
#         :return: 新的响应
#         """
#         doc = pq(response.text)
#         items = doc('.news-box .news-list li .txt-box h3 a').items() # 获取微信文章链接
#         for item in items():
#             url = item.attr('href')
#             weixin_request = WeinxinRequest(url=url,callback=self.parse_index)
#             yield weixin_request
#         next = doc('#sogou_next').attr('href') # 获取下一页链接
#         if next:
#             url = self.base_url + str(next)
#             weixin_request = WeinxinRequest(url=url,callback=self.parse_index,need_proxy=True)
#             yield weixin_request
#
#     def parse_detail(self,response):
#         """
#         解析详情页
#         :param response: 响应
#         :return: 微信公号文章
#         """
#         doc = pq(response.text)
#         data = {
#             'title':doc('.rich_media_title').text(),
#             'content':doc('.rich_media_content').text(),
#             'date':doc('#post-date').text(),
#             'nickname':doc('#js_profile_qrcode > div > strong').text(),
#             'wechat':doc('#js_profile_qrcode > div > p:nth-child(3) > span').text(),
#         }
#         yield data
#
#     def error(self,weixin_request):
#         """
#         错误处理
#         :param weixin_request: 请求
#         :return:
#         """
#         weixin_request.fail_time = weixin_request.fail_time + 1
#         print('Request Failed',weixin_request.fail_time,'Times',weixin_request.url)
#         if weixin_request.fail_time < MAX_FAILED_TIME:
#             self.queue.add(weixin_request)
#
#     def run(self):
#         """
#         程序入口
#         :return:
#         """
#         self.start()
#         self.schedule()
#
#
# if __name__ == '__main__':
#     spider = Spider()
#     spider.run()
#
#
# # 存储模块
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379
# REDIS_PASSWORD = None
# REDIS_KEY = 'weixin'
#
#
# import pymysql
# from config import *
#
# class MySQL():
#     def __init__(self,host=MYSQL_HOST,username=MYSQL_USER,password=MYSQL_PASSWORD,port=MYSQL_PORT,database=MYSQL_DATABASE):
#         """
#         MySQL初始化
#         :param host:
#         :param username:
#         :param password:
#         :param port:
#         :param database:
#         """
#         try:
#             self.db = pymysql.connect(host,username,password,database,charset='utf8',port=port)
#             self.cursor = self.db.cursor()
#         except pymysql.MySQLError as e:
#             print(e.args)
#
#     def insert(self,table,data):
#         """
#         插入数据
#         :param table:
#         :param data:
#         :return:
#         """
#         keys = ','.join(data.keys())
#         values = ','.join(['%s'] * len(data))
#         sql_query = 'insert into %s (%s) values (%s)' % (table,keys,values)
#         try:
#             self.cursor.execute(sql_query,tuple(data.values()))
#             self.db.commit()
#         except pymysql.MySQLError as e:
#             print(e.args)
#             self.db.rollback()
#
#
#
#
