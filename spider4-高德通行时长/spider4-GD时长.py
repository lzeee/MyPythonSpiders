# -*- coding: utf-8 -*-
# Time : 2019/7/12 12:27
# Author : shzgong@gmail.com
# File : get_data.py
# Description : 路径规划API

import os
import operator
import requests
import json
import time
from queue import Queue
from threading import Thread



global done
global keys
def read_keys():
    global keys
    keys = []
    with open('key.txt', 'r', encoding='utf-8') as f:
        info = f.readlines()
        for k in info:
            keys.append(k.strip('\n'))
    f.close()


# 生成url
def generate_url(start_lng, start_lat, end_lng, end_lat, time, method):
    start_lat = str(start_lat)
    start_lng = str(start_lng)
    end_lat = str(end_lat)
    end_lng = str(end_lng)
    if method == 'driving':
        url = 'https://restapi.amap.com/v3/direction/driving?origin=' + start_lng + ',' + start_lat + '&destination=' + end_lng + ',' + end_lat + '&output=json&time='+ time
    if method == 'integrated':
        url = 'https://restapi.amap.com/v3/direction/transit/integrated?origin=' + start_lng + ',' + start_lat + '&destination=' + end_lng + ',' + end_lat + '&nightflag=1&city=010&time=' + time + '&output=json'
    return url


class QueryTime(Thread):
    def __init__(self, queue, idx):
        Thread.__init__(self)
        self.queue = queue
        self.idx = idx
    def run(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            url, t, method, fid1, fid2 = item
            did = query_time(self, url, t, method, fid1, fid2)
            if not did:
                self.queue.put(item)
            self.queue.task_done()


# 获取查询结果
def get_time(worker, url, t, method, fid1, fid2):
    global done
    global keys
    try:
        url = url + '&key=' + keys[worker.idx]
        response = requests.get(url, timeout=1)
        data = json.loads(response.text)
        if data['infocode'] == '10000':
            if len(data['route']['transits']) == 0:
                result = [fid1, fid2, '-1']
            else:
                result = [fid1, fid2, data['route']['transits'][0]['duration']]
            with open(method + '_' + t.split(':')[0] + '_' + t.split(':')[1] + '.csv', 'a', encoding='utf-8', newline='') as f:
                f.write(','.join(result) + '\n')
            f.close()
            done += 1
            if done % 1000 == 0:
                print(done)
            return True
        else:
            print('Error:', data['infocode'])
            worker.idx += 1
            return False
    except:
        return False

def query_time(worker, url, t, method, fid1, fid2):
    result = get_time(worker, url, t, method, fid1, fid2)
    if not result:
        return False
    else:
        return True


# 调用高德API，计算通行时间
def calculate_travel_time(method):
    # 读取所有格网中心点的坐标
    center_points = {}
    with open('./shp_data/5th_ring_grid_center_GD.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for li in lines[1:]:
            fid, lng, lat = li.strip('\n').split(',')
            fid = fid.strip('"')
            center_points[fid] = [lat, lng]
    f.close()

    # 读取格子包含poi数量
    exclude_fid = []
    with open('./poi_data/5th_ring_grid_GD_poinum.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for li in lines[1:]:
            fid, num = li.strip('\n').split(',')
            fid = fid.strip('"')
            if num == '0':
                exclude_fid.append(fid)
    f.close()


    global done
    done = 0

    # 调用函数，计算时间
    valid_pair = []
    for fid1 in center_points.keys():
        for fid2 in center_points.keys():
            # 尽可能的排除，运算时间太长
            if fid1 == fid2 or cal_distance(center_points[fid1][1], center_points[fid1][0], center_points[fid2][1], center_points[fid2][0]) > 200:
                continue
            valid_pair.append([fid1, fid2])
    print(len(valid_pair), ' pair needs to be search.')

    search_list = []
    for t in ['8:00', '9:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00']:
        if not os.path.exists(method + '_' + t.split(':')[0] + '_' + t.split(':')[1] + '.csv'):
            with open(method + '_' + t.split(':')[0] + '_' + t.split(':')[1] + '.csv', 'w', encoding='utf-8') as f:
                f.write('start_id,end_id,time\n')
                f.close()
        for pair in valid_pair:
            start_lat = center_points[pair[0]][0]
            start_lng = center_points[pair[0]][1]
            end_lat = center_points[pair[1]][0]
            end_lng = center_points[pair[1]][1]
            url = generate_url(start_lng, start_lat, end_lng, end_lat, t, method)
            search_list.append([url, t, method, pair[0], pair[1]])
    print(len(search_list), ' query needs to be done.')

    queue = Queue()
    for x in range(8):
        worker = QueryTime(queue, x)
        worker.daemon = True
        worker.start()
    for s in search_list:
        queue.put(s)
        queue.join()


if __name__ == '__main__':
    calculate_travel_time()