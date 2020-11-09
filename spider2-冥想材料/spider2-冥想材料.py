# -*- coding: utf-8 -*-
# Time : 2019/4/24 20:22
# Author : shzgong@gmail.com
# File : spider.py
# Description : 爬meditation数据，自己听
# 流程：
# 确定每一大节的名称
# 包含小节的数量
# 确定每一节音频的名称
# 确定每一节音频的位置
# 爬取

import requests
from bs4 import BeautifulSoup
import os
import time
import lxml

def get_meditation():
    host = 'live.soundstrue.com'
    base_url = 'http://live.soundstrue.com/journeys/mindfulness-daily-free-gift/'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    # 直接手动复制登录之后的cookie
    cookie_str = 'live_access=%7B%22user%22%3A%221304309%22%7D; _gcl_au=1.1.77243089.1554971765; _ga=GA1.2.846266131.1554971765; _fbp=fb.1.1554971766135.1434384152; lc_sso8339831=1554971766257; __btr_em=c2h6Z29uZ0BnbWFpbC5jb20%3D; tid_7rurxl00clkk6pq1fwqc6j6yxh9mzs9t197jgtefvpplk7hy65=3.RM0.AzirZA.A-Ff.YL8N..uedn.b..s.eko.a.VT7bdQ.VT7ifQ.Cb9-gQ; mindfulness-daily-free-gift=1'
    cookies = {}
    for line in cookie_str.split(';'):
        name, value = line.strip().split('=')
        cookies[name] = value
    headers = {'user-Agent': user_agent, 'host': host}
    html = requests.get(base_url, headers=headers, cookies=cookies)
    soup = BeautifulSoup(html.text, features="lxml")
    subsubject = soup.find_all(attrs={"class":"sub-category-head"})
    subject_name = [x.text.strip() for x in subsubject]
    # print(subject_name)

    session_count = soup.find_all(attrs={"class":"session-buttons"})
    session_length = [len(x.find_all('li')) for x in session_count]
    # print(session_length)

    session_titles = soup.find_all(attrs={"class":"noselect"})
    session_title = [x['data-session-title'].strip().replace('+', '_') for x in session_titles[4:]]
    # print(session_title)

    count = 1
    for i in range(len(subject_name)):
        subject_path = './meditation/' + str(i+1)+'_' + subject_name[i].replace(' ', '_') + '/'
        if not os.path.exists(subject_path):
            os.mkdir(subject_path)
        for j in range(session_length[i]):
            url = 'http://soundstrue-ha.s3.amazonaws.com/oce/journeys/mindfulness_daily/audio/WC04753_' + str("%02d"%count) + '.mp3?AWSAccessKeyId=AKIAITC5TSWECGY4SOJQ'
            file_name = str(j+1) + '_' + session_title[count-1] + '.mp3'
            path = subject_path + '/' + file_name
            if not os.path.exists(path):
                res = requests.get(url)
                image_file = open(path, 'wb')
                for chunk in res.iter_content(100000):
                    image_file.write(chunk)
                image_file.close()
                print(count)
            count += 1
        print(subject_name[i], 'done')


if __name__ == '__main__':
    get_meditation()