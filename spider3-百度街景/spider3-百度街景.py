# -*- coding: utf-8 -*-
# Time : 2020/3/31 0:03
# Author : shzgong@gmail.com
# File : filter_StreetView.py
# Description : 筛选街景点的数据
# 放弃这套腾讯街景，改用百度街景数据

# 生成地铁站周围800米的wgs84点数据
# QGIS完成

# wgs84坐标转百度坐标系的投影坐标
# 每个地铁站对应一个文件
from urllib.request import urlopen
import json
import time
def WGS84_to_BD09_prj():
    # 读取所有采样点的WGS84坐标
    # 用field1的地铁站名字作为key
    # 存成每个地铁站对应的采样点的百度坐标
    sampling_points_WGS84 = {}
    with open('sampling_points_WGS84.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]
        for li in lines:
            station_name, lng, lat = li.strip('\n').split(',')
            if station_name in sampling_points_WGS84.keys():
                sampling_points_WGS84[station_name].append([lng, lat])
            else:
                sampling_points_WGS84[station_name] = []
    f.close()

    # 依次转换并保存
    for station_name in sampling_points_WGS84.keys():
        points_list = sampling_points_WGS84[station_name]
        convert_points_list = []
        while len(points_list) > 0:
            if len(points_list) > 20:
                coors = points_list[:21]
                points_list = points_list[21:]
            else:
                coors = points_list
                points_list = []
            coords_str = ''
            for pair in coors:
                coords_str = coords_str + ';' + pair[0] + ',' + pair[1]
            coords_str = coords_str[1:]
            key = 'kyIPiaAaKIxWHKhD0GUwoYUq'
            url = 'http://api.map.baidu.com/geoconv/v1/?coords=' + coords_str +  '&from=1&to=6&output=json&ak=' + key
            req = urlopen(url)
            res = req.read().decode()
            temp = json.loads(res)
            if temp['status'] == 0:
                results = temp['result']
                print(len(results))
                for i in range(len(results)):
                    baidu_x = temp['result'][i]['x']
                    baidu_y = temp['result'][i]['y']
                    convert_points_list.append([baidu_x, baidu_y])
            else:
                print(temp)
            time.sleep(0.1)
        with open('./StreetView_filtered/SamplePointsBD/' + station_name + '.csv', 'w', encoding='utf-8', newline='') as f:
            for pair in convert_points_list:
                f.write(','.join([str(x) for x in pair]) + '\n')
        f.close()
        print(station_name)
    return


# 对于每个地铁站，搜索附近的街景id
# 每个地铁站保存一个文件，注意去重
import os
def search_for_panoids():
    # 遍历每一个地铁站的采样点
    # 对每一个采样点搜索附近的全景照片，注意去重
    # 保存照片的id以及x和y
    # 其中id用来下载照片，x和y之后用来反算出街景点的WGS84经纬度
    sp_p = '../StreetView_filtered/SamplePointsBD/'
    files = os.listdir(sp_p)
    for file in files:
        print(file)
        panoids = {}
        with open(sp_p + file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for li in lines:
                x, y = li.strip('\n').split(',')
                url = 'https://mapsv0.bdimg.com/?qt=qsdata&x=' + x + '&y=' + y
                req = urlopen(url)
                res = req.read().decode()
                temp = json.loads(res)
                if temp['result']['error'] == 0:
                    result = temp['content']
                    pid = result['id']
                    baidu_x = result['x']
                    baidu_y = result['y']
                    panoids[pid] = [baidu_x, baidu_y]
                else:
                    print(temp)
                time.sleep(0.05)
        f.close()
        with open('./StreetView_filtered/Panoids/' + file, 'w', encoding='utf-8', newline='') as f:
            for pid in panoids.keys():
                f.write(pid + ',' + str(panoids[pid][0]) + ',' + str(panoids[pid][1]) + '\n')
        f.close()
    return


# 多线程爬取所有保存的街景照片
# 每个地铁站保存一个文件夹，每张图片4个方向
def download_all_images():
    # 遍历每一个地铁站对应的街景点
    # 四个方向都下载，保存在文件夹中，图片大小
    sp_p = '../StreetView_filtered/Panoids/'
    files = os.listdir(sp_p)
    exist = 0
    need_download_list = []
    for file in files:
        station = file.split('.')[0]
        # 创建文件夹
        if not os.path.exists('../StreetView_filtered/StreetViewImage/' + station + '/'):
            os.mkdir('../StreetView_filtered/StreetViewImage/' + station + '/')
        with open(sp_p + file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for li in lines:
                pid, x, y = li.strip('\n').split(',')
                angle = ['0', '90', '180', '270']
                for i in range(4):
                    image_id = pid + '_' + angle[i] + '.jpg'
                    path = '../StreetView_filtered/StreetViewImage/' + station + '/' + image_id
                    if os.path.exists(path):
                        exist += 1
                    else:  # 没有的则调用API下载
                        url = 'https://mapsv0.bdimg.com/?qt=pr3d&fovy=50&quality=100&panoid=' + pid + '&heading=' + angle[i] + '&pitch=0&width=1024&height=400'
                        need_download_list.append([url, path])
        f.close()
    print('need download image: ', len(need_download_list))
    print('already exist image: ', exist)
    return
    queue = Queue()
    for x in range(8):
        worker = DownloadImage(queue)
        worker.daemon = True
        worker.start()
    for img in need_download_list:
        queue.put(img)
    queue.join()
    return


import os
import requests
from queue import Queue
from threading import Thread

class DownloadImage(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
    def run(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            url, path = item
            download_image(url, path)
            self.queue.task_done()

def download_image(url, file_path):
    if os.path.exists(file_path):
        return
    else:
        try:
            while(1):
                headers = {
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
                            'Cache-Control': 'max-age=0',
                            'Connection': 'keep-alive',
                            'Host': 'mapsv0.bdimg.com',
                            'Sec-Fetch-Dest': 'document',
                            'Sec-Fetch-Mode': 'navigate',
                            'Sec-Fetch-Site': 'none',
                            'Sec-Fetch-User': '?1',
                            'Upgrade-Insecure-Requests': '1',
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
                            }
                images = requests.get(url,headers)
                img = images.content
                if images.status_code == 200:
                    with open(file_path, 'wb') as fp:
                        fp.write(img)
                    fp.close()
                print('下载成功!')
                break
        except:
            time.sleep(1)
            print("下载失败，重试...")


if __name__ == '__main__':
    download_all_images()