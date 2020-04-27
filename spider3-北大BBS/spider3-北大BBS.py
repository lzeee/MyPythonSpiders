# -*- coding: utf-8 -*-
# 0.
# 模拟登录，获取session

# 1.
# 爬取十大的帖子
# 所有文本内容，正则分词给出关键词
# 参与讨论的用户，查看用户的特点

# 2.
# 爬取所有版面
# 每个版面当前在线人数，倒叙排序，显示总贴数
# 点击之后显示，该版面的发帖数量随时间的变化，爬取10页，数量太多太慢


from flask import Flask,render_template,jsonify
import hashlib
import requests
from requests import RequestException
import json
from bs4 import BeautifulSoup
import lxml
from jieba import analyse
import re
from threading import Timer, Thread
from time import sleep
import collections

global global_data
global id
global psw
global period
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'}


# 需要填写的参数
want_page_num = 2 # 爬取板块时，要爬几页，多了会等一段时间, >=2
period = 10
id = ''
psw = ''


app = Flask(__name__)

# 0.
# 模拟登录，获取session
def get_session(usr_name, usr_psw):
    o = str(hashlib.md5((usr_psw + usr_name + usr_psw).encode(encoding='UTF-8')).hexdigest()).lower()
    data = {
        'username': usr_name,
        'password': usr_psw,
        'keepalive': 1,
        't': o,
    }
    try:
        session = requests.session()
        post = session.post('https://bbs.pku.edu.cn/v2/ajax/login.php', data=data, headers=headers)
        if post.status_code == 200:
            status = json.loads(post.text)['success']
            if status is True:
                print('Get session succeed.')
                return session
            else:
                print('Check your name and password.')
                return None
        else:
            print('Request failed.')
            return None
    except RequestException:
        print('Request failed.')
        return None


# 1.
# 分析十大内容
def analyse_big_ten(session, text):
    soup = BeautifulSoup(text, features="lxml")
    big_ten_section = soup.find_all("section",class_='topic-block big-ten')[0]
    big_ten_li = big_ten_section.find_all('li')
    result = {}
    for li in big_ten_li:
        info = {}
        idx = li.find('span', class_='rank-digit').get_text()
        href_name = li.find('a', class_='topic-link').get_text()
        post_name = li.find('a', class_='post-link').get_text()
        post_url = 'https://bbs.pku.edu.cn/v2/' + li.find('a', class_='post-link')['href']
        key_words = analyse_key_word_of_post(session, post_url)
        gender, rankname = analyse_user_info_of_post(session, post_url)
        info["keywords"] = key_words
        info["gender"] = gender
        info["rankname"] = rankname
        info['id'] = idx
        info['section'] = href_name
        info['title'] = post_name
        info['url'] = post_url
        result[idx] = info
    return result


# 分析帖子内发言的关键词
def analyse_key_word_of_post(session, url, number=10):
    # 每个帖子返回k个关键词，字符云
    # 获取所有的发言内容
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, features="lxml")
    page_count = int(soup.find('div', class_='paging paging-top').find_all('div')[-2].get_text().split(' ')[1])
    data = []
    for page_idx in range(1, page_count+1):
        a_url = url + '&page=' + str(page_idx)
        a_response = session.get(a_url, headers=headers)
        a_soup = BeautifulSoup(a_response.text, features="lxml")
        text_div = a_soup.find_all('div', class_='body file-read image-click-view')
        text_p = []
        for div in text_div:
            p = div.find('p')
            if p.get('class') == None:
                text_p.append(p)
        text_p = [p.get_text() for p in text_p]
        for d in text_p:
            data.append(d)
    # 解析发言内容，返回关键词
    rule = re.compile(u"[^a-zA-Z0-9\u4e00-\u9fa5]")
    for line in data:
        line = rule.sub('',line)
    data_text = '。'.join(data)
    key_words = analyse.textrank(data_text)
    return key_words[:number]


# 分析帖子内参与讨论的用户特点
def analyse_user_info_of_post(session, url):
    # 用户的性别占比，等级占比，饼状图
    # 获取在该帖子内发言的所有用户id
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, features="lxml")
    page_count = int(soup.find('div', class_='paging paging-top').find_all('div')[-2].get_text().split(' ')[1])
    id = []
    for page_idx in range(1, page_count+1):
        a_url = url + '&page=' + str(page_idx)
        a_response = session.get(a_url, headers=headers)
        a_soup = BeautifulSoup(a_response.text, features="lxml")
        name_ps = a_soup.find_all('p', class_='username')
        name_as = [p.a for p in name_ps if p]
        names = [a.get_text() for a in name_as if a]
        for n in names:
            if n !='' and n!='Anonymous' and n not in id:
                id.append(n)
    # 获取所有用户的信息，用户信息结果示例
    # F,M,-
    '''
    {"success": true, "
        result": [
        {"id": 6090,
        "username": "piaimu",
        "nickname": [{}],
        "nickname_raw": "jiajia",
        "gender": "F", ———————————————————性别
        "horoscope": "",
        "lastlogin": 1559390034,
        "lastlogout": 1518609408,
        "ip": 1219499180,
        "numlogins": 1776,—————————————————登录次数
        "numposts": 10,——————————————————发帖次数
        "rating": 0,
        "value": 119,
        "score": 1.1457409259259, "ranksys": 0,
        "rankname": "\u4e00\u822c\u7ad9\u53cb", "group": 12, "groupname": "",
        "avatar": "images\/user\/portrait-fem.png"}]}
    '''
    id_str = ['"'+ x + '"' for x in id]
    data = {'names':'[' + ','.join(id_str) + ']'}
    base_url = 'https://bbs.pku.edu.cn/v2/ajax/get_userinfo_by_names.php'
    response = session.post(base_url, data, headers=headers)
    # 性别占比饼状图
    gender = {}
    rankname = {}
    if response.status_code == 200:
        query_dict = json.loads(response.text)
        if query_dict['success'] == True:
            infos = query_dict['result']
            for info in infos:
                g = info['gender']
                r = info['rankname']
                if g in gender.keys():
                    gender[g] += 1
                else:
                    gender[g] = 1
                if r in rankname.keys():
                    rankname[r] += 1
                else:
                    rankname[r] = 1
    # {'M': 18, '-': 10, 'F': 3}
    # {'亚洲': 1, '一般站友': 9, '昆吾': 1, '主序星': 2, '高级站友': 3, '仓鼠': 1, '浣熊': 2, '巡抚': 1, '兔斯基': 1, '巨阙': 1, '水滴': 1, '树袋熊': 1, '六耳猕猴': 1, '龙泉': 1, '剑豪': 1, '流氓兔': 1, '老站友': 1, '剑客': 1, '新手上路': 1}
    return gender, rankname


# 2.
# 分析版面信息
def analyse_block(session, text):
    soup = BeautifulSoup(text, features="lxml")
    hot_block_section = soup.find("div", class_='column-right').find("section")
    hot_block_li = hot_block_section.find_all('li')
    idx = 1
    result = {}
    for li in hot_block_li:
        info = {}
        info['title'] = li.a.get_text()
        info['rank'] = idx
        url = 'https://bbs.pku.edu.cn/v2/' + li.a['href']
        info['url'] = url
        info['online'], info['postcount'] = get_block_stat(session, url)
        info['post'] = get_block_post(session, url)
        result[idx] = info
        idx += 1
    return result


# 获取在线人数和总帖数
def get_block_stat(session, url):
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, features="lxml")
    stat_div = soup.find('div',id='stat')
    stat_span = stat_div.find_all('span')
    online = stat_span[0].get_text()
    postcount = stat_span[-1].get_text()
    return online, postcount


# 获取版面历史发表数据信息
def get_block_post(session, url):
    # 获取总页数
    global want_page_num
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, features="lxml")
    page_count = int(soup.find('div', class_='paging').find_all('div')[-2].get_text().split(' ')[1])
    # 遍历每一页
    post_info = {}
    base_url = 'https://bbs.pku.edu.cn/v2/'
    # 页数过多，速度过慢
    for page in range(1, 1 + want_page_num):
        a_url = url + "&page=" + str(page)
        a_response = session.get(a_url, headers=headers)
        a_soup = BeautifulSoup(a_response.text, features='lxml')
        # 获取每个帖子的链接
        list_div = a_soup.find_all('div', class_='list-item-topic list-item')
        url_list = []
        for div in list_div:
            url_list.append(base_url+ div.a['href'])
        # 访问并获取发帖时间
        for post_url in url_list:
            b_response = session.get(post_url, headers=headers)
            b_soup = BeautifulSoup(b_response.text, features='lxml')
            time = b_soup.find_all('div',class_='sl-triangle-container')[0].span.span.get_text()
            if "最后"in time:
                time = time[5:].split(' ')[0]
            else:
                time = time[3:].split(' ')[0]
            if "于" in time:
                time = time[1:]

            # 用时间组织数据，时间按天切分
            if time in post_info.keys():
                post_info[time] += 1
            else:
                post_info[time] = 1
    post_info = collections.OrderedDict(sorted(post_info.items(), key=lambda  x:x[0]))
    return post_info


def get_bbs_data():
    global id
    global psw
    global global_data
    print('Getting data...')
    session = get_session(id,psw)
    if session is not None:
        response = session.get('https://bbs.pku.edu.cn/v2/home.php', headers=headers)
        info1 = analyse_big_ten(session, response.text)
        info2 = analyse_block(session, response.text)
        global_data['1'] = info1
        global_data['2'] = info2
        print('Get data done.')
    else:
        print('Get data error.')


# 参考代码，实现flask定时更新数据
# https://gist.github.com/chadselph/4ff85c8c4f68aa105f4b
class Scheduler(object):
    def __init__(self, sleep_time, function):
        self.sleep_time = sleep_time
        self.function = function
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception("this timer is already running")

    def _run(self):
        self.function()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None


@app.route('/')
def get_web():
    return render_template('index.html')



@app.route('/get_data')
def get_data():
    global global_data
    return jsonify(global_data)



if __name__ == '__main__':
    # 程序最开始先分析得到一次数据
    # 因为要爬取的数据比较多，所以取一次数据大概要4分钟，
    global global_data
    global_data = {}
    get_bbs_data()
    # 之后网页服务器开始运行每10分钟执行一次，刷新data
    period = 10
    scheduler = Scheduler(60*period, get_bbs_data)
    scheduler.start()
    app.run(host='0.0.0.0', debug=False)
    scheduler.stop()