# -*- coding: utf-8 -*-
# Time : 2019/5/24 11:56
# Author : shzgong@gmail.com
# File : youtube_easy_downloader.py
# Description : 爬取youtube视频

import os
import requests
import bs4
from bs4 import BeautifulSoup
import urllib.request
import lxml
import time
import json
import pysrt
import re
import xml.dom.minidom
from xml.dom.minidom import parseString

def is_pure_num(content):
    try:
        content = int(content)
    except:
        return False
    return True


def get_srt(video_id, save_path, file_name):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"
    file_name = re.sub(rstr, "_", file_name)
    path = save_path + '/' + file_name
    if os.path.exists(path):
        print(file_name, ' scripts download already done.')
        return
    url = 'https://downsub.com/?url=https://www.youtube.com/watch?v=' + video_id
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features="lxml")
        english_url = 'https://downsub.com' + soup.find_all('a', text=">>Download<<")[0]['href'][1:]
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla / 5.0 (Windows NT 6.1; WOW64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 36.0.1941.0 Safari / 537.36')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(english_url, path)
        print(file_name, ' download done')


def get_video(video_id, save_path, file_name):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"
    file_name = re.sub(rstr, "_", file_name)
    path = save_path + '/' + file_name
    if os.path.exists(path):
        print(file_name, ' video download already done.')
        return
    url = "https://ytoffline.net/download/?url=https://www.youtube.com/watch?v="+video_id
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='lxml')
    trs = soup.find('table', class_='downloads-table').find_all('tr')
    tds = trs[1].find_all('td')
    video_url = tds[2].a['href']
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent','Mozilla / 5.0 (Windows NT 6.1; WOW64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 36.0.1941.0 Safari / 537.36')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(video_url, path)
    print(file_name, ' video download done.')


def download_video(video_id, save_path, file):
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    get_srt(video_id, save_path, file + '.srt')
    get_video(video_id, save_path, file + '.mp4')
    return


def download_playlist(playlist_id, save_path):
    # 解析id以及name
    playlist_url = 'https://api.youtubemultidownloader.com/playlist?url=https%3A%2F%2Fwww.youtube.com%2Fplaylist%3Flist%3D' + playlist_id
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Origin': 'https://youtubemultidownloader.net',
               'Referer': 'https://youtubemultidownloader.net/playlists.html',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
    response = requests.get(playlist_url, headers=headers)
    playlist_info = json.loads(response.text)['items']
    for video_info in playlist_info:
        c_id = video_info['id']
        cv_name = video_info['title']
        download_video(c_id, save_path, cv_name)
    return


if __name__ == '__main__':
    download_video('_FIIQwck7gU', './', '常用的地道英语口语练习')
