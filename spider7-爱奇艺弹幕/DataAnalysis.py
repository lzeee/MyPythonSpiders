# -*- coding: utf-8 -*-

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from collections import  OrderedDict
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

base_path = 'BulletInfo/'
bullet_dis = 'img_dis/'
sentiment_path = 'BulletInfoOutput/'
sentiment_dis = 'setiment_dis/'


# 1.每一集内弹幕数量频率分布
# 参数是以多少分钟为间隔
def bullet_distribution_of_each_episode(interval = 2):
    files = os.listdir(base_path)
    for file in files:
        plt.clf()
        plt.cla()
        episode_id = file.split('.')[0].split(' ')[1]
        title = "延禧攻略第" + episode_id + "集弹幕频率图"
        file_path = os.path.join(base_path, file)
        save_path = os.path.join(bullet_dis, title+'.jpg')
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for line in reader:
                if reader.line_num == 1:
                    continue
                else:
                    time, content = line
                    data.append(int(time))
        f.close()
        draw = []
        interval_count = max(data)//(interval*60) + 1
        for sec in data:
            current_minute = sec//(interval*60) + 1
            draw.append(current_minute)
        mu = np.mean(draw)
        sigma = np.std(draw)
        n, bins, patches = plt.hist(draw,
                 density=True, # 频率图
                 bins=interval_count,
                 rwidth=1,
                 alpha=0.8,
                 edgecolor='white',
                 )
        y = mlab.normpdf(bins, mu, sigma)  # 用最接近的正太曲线去拟合，理论上感觉是正态曲线
        plt.plot(bins, y, 'y--')
        plt.xlabel("Time (interval:"+str(interval)+ ' minutes)')
        plt.ylabel("Bullet Frequency(%)")
        plt.title(title)
        plt.savefig(save_path)


# 2.整部电视剧的弹幕分布频率情况
def bullet_distribution_of_all():
    files = os.listdir(base_path)
    output = "./延禧攻略 弹幕数量变化图.jpg"
    title = "延禧攻略 弹幕数量变化图"
    bullet_num = {}
    for file in files:
        file_path = os.path.join(base_path, file)
        episode_id = int(file.split('.')[0].split(' ')[1])
        with open(file_path, 'r', encoding='utf-8') as f:
            bullet_count = len(f.readlines()) - 1
            bullet_num[episode_id] = bullet_count
        f.close()
    bullet_num = OrderedDict(sorted(bullet_num.items(),key= lambda x:x[0]))
    plt.xlabel("电视剧集")
    plt.ylabel("弹幕总条数")
    plt.title(title)
    x = list(bullet_num.keys())
    y = list(bullet_num.values())
    plt.bar([z for z in x], y, alpha=0.8)
    plt.ylim((14500,16500))
    plt.savefig(output)


# 3.每一集内情感变化
# 参数是以多少分钟为间隔
def emotion_of_each_episode(interval = 2):
    files = os.listdir(sentiment_path)
    for file in files:
        plt.clf()
        plt.cla()
        episode_id = file.split('.')[0].split(' ')[1]
        title = "延禧攻略第" + episode_id + "集情感变化图"
        file_path = os.path.join(sentiment_path, file)
        save_path = os.path.join(sentiment_dis, title + '.jpg')
        sentiment_p = {}
        sentiment_n = {}
        sentiment_add = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for line in reader:
                try:
                    time, content, p, n, confidence, clas = line
                    time = int(time)
                    p = float(p)
                    n = float(n)
                    add = p-n
                    current_idx = time//(interval*60) + 1
                    if current_idx in sentiment_p.keys():
                        sentiment_p[current_idx].append(p)
                        sentiment_n[current_idx].append(-n)
                        sentiment_add[current_idx].append(add)
                    else:
                        sentiment_p[current_idx] = [p]
                        sentiment_n[current_idx] = [-n]
                        sentiment_add[current_idx] = [add]
                except:
                    continue
        f.close()
        sentiment_p = OrderedDict(sorted(sentiment_p.items(),key=lambda x:x[0]))
        sentiment_n = OrderedDict(sorted(sentiment_n.items(), key=lambda x: x[0]))
        sentiment_add = OrderedDict(sorted(sentiment_add.items(), key=lambda x: x[0]))

        x = list(sentiment_add.keys())
        y_p = [np.mean(item) for item in list(sentiment_p.values())]
        y_n = [np.mean(item) for item in list(sentiment_n.values())]
        y_add = [np.mean(item) for item in list(sentiment_add.values())]
        plt.plot(x,y_p,color='g',label='positive_possibility')
        plt.plot(x,y_n,color='r', label='negative_possibility')
        plt.plot(x,y_add, color='c', label='positive-negative')
        plt.legend()
        plt.xlabel("Time (interval:"+str(interval)+ ' minutes)')
        plt.ylabel("Sentiment")
        plt.title(title)
        plt.gca().spines['bottom'].set_position('center')
        plt.gca().spines['top'].set_color('none')
        plt.gca().spines['right'].set_color('none')
        plt.ylim((-1,1))
        plt.savefig(save_path)


# 4.整部点数据的情感变化
def emotion_of_all():
    files = os.listdir(sentiment_path)
    sentiment_p = {}
    sentiment_n = {}
    sentiment_add = {}
    title = "延禧攻略 弹幕情感变化图"
    output = "./延禧攻略 弹幕数量变化图.jpg"
    for file in files:
        data_p = []
        data_n = []
        data_add = []
        episode_id = int(file.split('.')[0].split(' ')[1])
        file_path = os.path.join(sentiment_path, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for line in reader:
                try:
                    time, content, p, n, p3, p4 = line
                    data_p.append(float(p))
                    data_n.append(-float(n))
                    data_add.append(float(p)-float(n))
                except:
                    continue
        f.close()
        sentiment_p[episode_id] = np.mean(data_p)
        sentiment_n[episode_id] = np.mean(data_n)
        sentiment_add[episode_id] = np.mean(data_add)
    sentiment_n = OrderedDict(sorted(sentiment_n.items(),key=lambda x:x[0]))
    sentiment_p = OrderedDict(sorted(sentiment_p.items(), key=lambda x: x[0]))
    sentiment_add = OrderedDict(sorted(sentiment_add.items(), key=lambda x: x[0]))

    plt.xlabel("电视剧集")
    plt.ylabel("情感变化")
    plt.title(title)
    x = list(sentiment_add.keys())
    y_p = list(sentiment_p.values())
    y_n = list(sentiment_n.values())
    y_add = list(sentiment_add.values())
    plt.plot(x, y_p, color='g', label='positive_possibility')
    plt.plot(x, y_n, color='r', label='negative_possibility')
    plt.plot(x, y_add, color='c', label='positive-negative')
    plt.legend()
    plt.gca().spines['bottom'].set_position('center')
    plt.gca().spines['top'].set_color('none')
    plt.gca().spines['right'].set_color('none')
    plt.ylim((-1, 1))
    plt.xticks(np.arange(0, 71, 5))
    plt.savefig(output)


if __name__ == '__main__':
    emotion_of_all()