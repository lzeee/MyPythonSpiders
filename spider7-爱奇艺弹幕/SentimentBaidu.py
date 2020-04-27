import requests
import json
import re
import time
from queue import Queue
from threading import Thread
import os
import csv

# 多线程下载
# 从github偷的
tokens = ['24.0205d6735ddd847669e9b3785728af6f.2592000.1561896125.282335-16398202',
          '24.1c2540099fa5747a63888d0e574542a9.2592000.1561896169.282335-16408310',
          '24.7e5c0ba1ee15f7c8a0a3b733869b035b.2592000.1561898059.282335-16057417',
          '24.9ff5ae3c3448070b59ed8b1da06c11cf.2592000.1561898288.282335-11245226',
          '24.cfb0ff6b392a41cb55f0b8c034a85bd5.2592000.1561898566.282335-14393081',
          '24.164d9c00ff9532489878656e3e7986c2.2592000.1561898641.282335-15857310',
          '24.353c9323d04ef08765bccfbbd7e6d998.2592000.1561899089.282335-11626199',
          '24.0533a4d0b29f81143c324f1df558a4a8.2592000.1561899135.282335-11671432',
          '24.afa76402976383f78c4a83c148dee92d.2592000.1561899303.282335-9734157',
          '24.f3826e8233ff86c15266513061d74cc5.2592000.1561899464.282335-15495481']


class QueryInfo(Thread):
    def __init__(self, queue, at):
        Thread.__init__(self)
        self.queue = queue
        self.Host = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token='
        self.at = at
        self.url = self.Host + self.at
        self.headers = {'Content-Type': 'application/json', 'Connection': 'close'}

    def run(self):
        while True:
            item = self.queue.get()
            if item is None:
                break
            t, origin_text, path = item
            time.sleep(0.12)
            try:
                self.query_setiment_info(t, origin_text, path)
                self.queue.task_done()
            except:
                self.queue.put(item)
                continue

    def query_setiment_info(self, t, origin_text, path):
            text = self.clean_comment(origin_text)
            raw = {'text': text}
            data = json.dumps(raw).encode('gbk')
            r = requests.post(url=self.url, data=data, headers=self.headers)
            if r != None:
                content = r.json()
                # 查看数据编码问题
                if content['items']:
                    contentposprob = content['items'][0]['positive_prob']
                    contentnegprob = content['items'][0]['negative_prob']
                    contentconfi = content['items'][0]['confidence']
                    contentsenti = content['items'][0]['sentiment']
                    with open(path, 'a+', encoding='utf-8') as f:
                        info = [int(t),origin_text,contentposprob,contentnegprob,contentconfi,contentsenti]
                        info = [str(x) for x in info]
                        f.write(",".join(info)+'\n')
                    f.close()
                else:
                    print('error')
            else:
                print('error')

    def clean_comment(self, text):
        emoji = re.compile(
                u'['
                u'\U0001F300-\U0001F64F'
                u'\U0001F680-\U0001F6FF'
                u'\u2600-\u2B55]+', re.UNICODE)
        text = re.sub(r"[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）:：]+", "",text)
        text = re.sub(emoji, '', text)
        return text


def get_ready_item():
    outputpath = 'BulletInfoOutput/'
    files = os.listdir(outputpath)
    result = []
    for file in files:
        output = outputpath + file
        with open(output, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for line in reader:
                try:
                    time, origi_text,p1,p2,p3,p4 = line
                    result.append([time, origi_text, output])
                except:
                    continue
        f.close()
    return result


def main():
    filepath = 'BulletInfo/'
    outputpath = 'BulletInfoOutput/'
    files = os.listdir(filepath)
    aleady = get_ready_item()
    print(len(aleady), ' done')
    to_do_list = []
    for file in files:
        check = True
        print(file)
        output = outputpath + file
        if not os.path.exists(output):
            f = open(output,'w',encoding='utf-8')
            f.close()
            check = False
        with open(filepath+file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for line in reader:
                if reader.line_num == 1:
                    continue
                else:
                    time, origi_text = line
                    item = [time, origi_text, output]
                    if check:
                        if item not in aleady:
                            to_do_list.append(item)
                    else:
                        to_do_list.append(item)
        f.close()
    print(len(to_do_list), ' need to be done')

    queue = Queue()
    for x in range(10):
        worker = QueryInfo(queue, tokens[x])
        worker.daemon = True
        worker.start()
    for info in to_do_list:
        queue.put(info)
    queue.join()



if __name__ == '__main__':
    main()