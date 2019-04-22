import requests
import time
from requests.packages import urllib3
import json
import threading

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'X-LC-Sign': '0265a19fbf93927cd40aadd0a5b97cab,1555058615117',
    'X-LC-Id': '9pq709je4y36ubi10xphdpovula77enqrz27idozgry7x644',
    'X-LC-Prod': '0',
    'Host': '9pq709je.engine.lncld.net'
}

# {"page":199,"perPage":132 }
# https://9pq709je.engine.lncld.net/1.1/call/getHotAuthorsIncludeCountByLikers


# {"page":3900,"perPage":100}
# https://9pq709je.engine.lncld.net/1.1/call/getWorksAllIncludeCount

dir_author = 'file/author/'
dir_article = 'file/article/'


def get_xcz_author(url):
    for start in range(1, 200):
        payload = {'page': start, 'perPage': 132}
        req = requests.post(url, headers=headers,
                            verify=False, data=json.dumps(payload))
        with open(dir_author + 'xcz_author_' + str(start) + '.json', 'w', encoding='utf-8') as f:
            f.write(req.text)
        print('------------存入作者数据：' + str(start) + '------------------')
        time.sleep(5)


def get_xcz_article(url):
    for start in range(4372, 5000):
        payload = {'page': start, 'perPage': 100}
        req = requests.post(url, headers=headers,
                            verify=False, data=json.dumps(payload))
        with open(dir_article + 'xcz_article_' + str(start) + '.json', 'w', encoding='utf-8') as f:
            f.write(req.text)
        print('------------存入文章数据：' + str(start) + '------------------')
        time.sleep(3)



if __name__ == "__main__":
    urllib3.disable_warnings()
    # t1 = threading.Thread(group=None, target=get_xcz_author, args=(
    #     'https://9pq709je.engine.lncld.net/1.1/call/getHotAuthorsIncludeCountByLikers',))
    t2 = threading.Thread(group=None, target=get_xcz_article, args=(
        'https://9pq709je.engine.lncld.net/1.1/call/getWorksAllIncludeCount',))
    # t1.start()
    t2.start()
