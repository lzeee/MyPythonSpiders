# -*- coding: UTF-8 -*-

import urllib.request
import re
import json
from random import randint
import zlib
import xml.etree.ElementTree as ET


class GetBulletInfo(object):
    def __init__(self, _urls):
        self.urls = _urls
        self.count = 0

    def get_response(self, url):
        req = urllib.request.Request(url)
        req.add_header(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 " +
            "(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36")
        response = urllib.request.urlopen(req).read()
        return response

    def output_bullet(self, url):
        # 获取网页信息
        page_info = json.loads(
            re.search(r'page-info=\'(.*)\' :video-info',
                      self.get_response(url).decode("utf-8")).group(1))
        duration_str = page_info['duration'].split(':')
        duration = 0
        for i in range(len(duration_str) - 1):
            duration = (duration + int(duration_str[i])) * 60
        duration = duration + int(duration_str[-1])
        albumid = page_info['albumId']
        tvid = page_info['tvId']
        categoryid = page_info['cid']
        page = duration // (60 * 5) + 1
        filename = 'BulletInfo/episode ' + str(self.count) + '.csv'
        # 输出到文件
        with open(filename, "w", encoding='utf-8') as fout:
            fout.write('time,content\n')
            for i in range(page):
                dec = zlib.decompressobj(32 + zlib.MAX_WBITS)
                b = dec.decompress(
                    self.get_response(
                        'http://cmts.iqiyi.com/bullet/' + str(tvid)[-4:-2] +
                        '/' + str(tvid)[-2:] + '/' + str(tvid) + '_300_' +
                        str(i + 1) + '.z?rn=0.' +
                        ''.join(["%s" % randint(0, 9)
                                 for num in range(0, 16)]) +
                        '&business=danmu&is_iqiyi=true' +
                        '&is_video_page=true&tvid=' + str(tvid) + '&albumid=' +
                        str(albumid) + '&categoryid=' + str(categoryid) +
                        '&qypid=01010021010000000000'))
                root = ET.fromstring(b.decode("utf-8"))
                for bulletInfo in root.iter('bulletInfo'):
                    timepoint = bulletInfo[2].text  # 弹幕发送时间
                    content = bulletInfo[1].text  # 弹幕内容
                    fout.write(str(timepoint) + ',"' + str(content) + '"\n')

    def run(self):
        for url in self.urls:
            self.count += 1
            print('collecting episode ' + str(self.count))
            self.output_bullet(url)


if __name__ == "__main__":
    urls = open('urls.txt', 'r', encoding='utf-8')
    GetBulletInfo(urls).run()
