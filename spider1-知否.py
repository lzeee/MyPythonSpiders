# -*- coding: utf-8 -*-
# Created on: 2019/2/19 22:04
# Author  : shzgong
# File    : spider-知否.py
# Comment : 尝试爬取小说网站上的一部小说

import time
import re
import urllib.request
from bs4 import BeautifulSoup

def get_novel():
    # 访问目录页面
    site = urllib.request.urlopen('http://www.luoxia.com/minglan/')
    html = site.read()
    html = html.decode('utf-8')  # 解码

    # 每章的标签形式如下，有两种格式的段落标签，应该是为了反爬
    # <a target="_blank" title="x" href="y">x</a>
    # <b title="第44回 她将来会嫁谁？" onclick="window.open('http://www.luoxia.com/minglan/55839.htm')">第44回 她将来会嫁谁？</b>
    reg1 = r'<a target="_blank" title="(.*?)" href="(.*?)">.*?</a>'
    reg2 = r'<b title="(.*?)" onclick="window.open(.*?)">.*?</b>'
    urls1 = re.findall(reg1,html)
    urls2 = re.findall(reg2,html)
    urls = urls1 + [(title,url[2:-2]) for title,url in urls2]
    urls = list(urls)
    sum = len(urls)
    count = 0
    while(len(urls)>0):
        title,url = urls[0]
        try:
            f = open('知否\{}.txt'.format(title), 'w',encoding='utf-8')
            f.write(title + '\n')
            site = urllib.request.urlopen(url,timeout=5)
            html = site.read().decode("utf-8")
            soup = BeautifulSoup(html,'lxml')
            div = soup.find('div',id='nr1')
            ps = div.find_all('p')
            for p in ps:
                # 去掉一些没用的段落
                if  p.string == None or "公众号" in p.string or re.search(r'.*?落.*?霞.*?小.*?',p.string):
                    continue
                else:
                    f.write(p.string + '\n')
            f.close()
            count += 1
            print("%.2f%% has been downloaded."%(count*100./sum))
            urls.pop(0)
        except:
            time.sleep(0.1)
            continue

if __name__ == '__main__':
    get_novel()