# 爬取新浪国内多页最新新闻
# 使用pandas分析
# -*- coding: utf-8 -*-
import requests
import json
from bs4 import BeautifulSoup
import pandas


# 函数：先提取该则新闻的news_id,然后拼接到公共相同的comment_url中
#      然后，根据拼接的url获取动态加载的评论数
# 参数：每则新闻的链接news_url
def getCommentCounts(news_url):
    comment_url = 'https://comment.sina.com.cn/page/info?version=1&format=json&channel=gn&newsid=comos-{}&group=undefined&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=3&t_size=3&h_size=3' # 使用大括号
    news_id = news_url.split('/')[-1].rstrip('.shtml').lstrip('doc-i')
    # 也可以通过正则表达式来获取news_id
    # m = re.search('doc-i(.*).shtml', news_url)
    # news_id = m.group(1)
    comments = requests.get(comment_url.format(news_id))  # 将news_id放到comment_url中,获取评论的数据
    jd = json.loads(comments.text)
    return jd['result']['count']['total']  # 返回评论数


# 函数：获取每则新闻的详细信息
# 参数：每则新闻的链接：news_url
def getNewsDetail(news_url):
    results = {}  # 存储结果
    res = requests.get(news_url)  # 获取新闻页面
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')  # 解析
    results['title'] = soup.select('.main-title')[0].text  # 取标题
    results['date'] = soup.select('.date')[0].text  # 提取时间
    results['source'] = soup.select('.source')[0].text  # 提取来源

    article = []
    # 提取新闻内容，因为倒数第一个<p>是责任编辑，要去掉
    for p in soup.select('#article p')[:-1]:
        article.append(p.text.strip())

    results['article'] = ' '.join(article)  # 新闻内容连接成字符串，存到results中
    # 取倒数第一个<p>标签中的内容,即责任编辑
    results['editor'] = soup.select(".show_author")[0].text.strip('责任编辑：')
    results['counts'] = getCommentCounts(news_url)  # 获取评论数
    return results


# 函数：先根据动态加载每页最新新闻的js_url来获取该页的20个新闻url
#      然后，根据该则新闻url，整合改则新闻的所需内容
# 参数：js_url,
def getNews(js_url):
    newsDetails = []  # 存储每则新闻的内容
    res = requests.get(js_url)
    jd = json.loads(res.text.replace('try{feedCardJsonpCallback(', ' ').replace(');}catch(e){};', ' ')) # 把最前面和最后面try..catch去掉
    for ent in jd['result']['data']:
        newsDetails.append(getNewsDetail(ent['url']))  # 先得到每则具体新闻的链接，然后获取该则新闻的内容
    return newsDetails  # 返回20则新闻的内容


if __name__ == "__main__":
    news_total = []
    # 动态加载每页新闻的链接
    common_js_url = 'https://feed.sina.com.cn/api/roll/get?pageid=121&lid=1356&num=20&versionNumber=1.2.4&page={}&encode=utf-8&callback=feedCardJsonpCallback&_=1543025692074'
    for i in range(1, 10):
        js_url = common_js_url.format(i)  # 把页数拼接到common_js_url
        content = getNews(js_url)  # 最新新闻的每页新闻：20个,合并新闻信息
        news_total.extend(content)
    # 使用pandas分析
    df = pandas.DataFrame(news_total)
    df.to_excel('news.xlsx')  # 保存到excel表中
