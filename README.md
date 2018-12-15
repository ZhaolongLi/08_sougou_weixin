# 08_sougou_weixin
爬取内容：
  搜狗微信文章
网站反爬措施：
  监测IP访问频率，高频率的IP封杀
请求库：
  requests,urllib
解析库：
  pyquery
存储数据：
  MySQL
其他技术：
  构建代理池，每次请求更换一个IP
  采用Redis构建一个请求队列，从请求队列里取请求
 
