import requests
import time
from requests.packages import urllib3
import json
import threading
import os
from lxml import etree
import traceback

headers = {
'Host': 'www.juzimi.com',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
}
# https://www.juzimi.com/ju/*
# //div[@id='xqtitle']/a 当前页句子迷
# //div[@class='nextlinks']/a[@class='goto-previous-node']  下一页


# //a[@rel='tag']   第一个作者，第二个文章
# //div[@class='jianjietitle']/h2/strong 人名
# //div[@class='xqjianjieagewr'] 基本信息
# //div[@class='jianjiecontext'] 简介

# //div[contains(@class,'comment-publish')] 句子评论
# //a[@class='wridescjiajie']

def get_value(items, str, type='text'):
    for i in items:
        try:
            if str == 'text':
                return (i.text if type == 'text' else etree.tostring(i, method='html', encoding="utf-8").decode('utf-8'))
            else:
                return i.attrib[str]
        except Exception as e:
            if not os.path.exists('file/log/' + time.strftime("%Y-%m-%d") + '/'):
                os.makedirs('file/log/' + time.strftime("%Y-%m-%d") + '/')
            with open('file/log/' + time.strftime("%Y-%m-%d") + '/' + time.strftime("%H") + '.log', 'w', encoding='utf-8') as fs:
                fs.write('-------' + time.strftime("%H_%M_%S") + '----' + traceback.format_exc() +
                         '---:  (' + str + ')' + etree.tostring(i, method='html', encoding="utf-8").decode('utf-8'))
    return ''

def get_jzm_author(start):
    w_url = "https://www.juzimi.com" + start
    w_req = requests.get(w_url,headers=headers,verify=False)
    w_html = etree.HTML(w_req.text, etree.HTMLParser())
    j_url = get_value(w_html.xpath("//a[@class='wridescjiajie']"),'href')
    if j_url.strip() != '':
        j_req = requests.get("https://www.juzimi.com" + j_url)
        j_html = etree.HTML(j_req.text, etree.HTMLParser())
        author_object = {"url": "https://www.juzimi.com" + j_url, "id": j_url.replace('/jianjie/','')}
        author_object["name"] = get_value(j_html.xpath("//div[@class='jianjietitle']/h2/strong"),'text')
        author_object["base"] = get_value(j_html.xpath("//div[@class='xqjianjieagewr']"),'text')
        author_object["intro"] = get_value(j_html.xpath("//div[@class='jianjiecontext']"),'text')
        text = json.dumps(author_object, ensure_ascii=False)
        ct = j_url.replace('/','')
        with open('file/author/author_' + ct + '.json', 'w', encoding='utf-8') as fs:
           fs.write(text)
        print('---------------存入作者数据:'+ ct + '------------------------------')
        time.sleep(4)


def get_jzm_ju(start):
    b_url = "https://www.juzimi.com/ju/" + start
    req = requests.get(b_url,headers=headers,verify=False)
    html = etree.HTML(req.text, etree.HTMLParser())
    juzi_object = {"url": b_url, "id": start}

    juzi_object["contentHtml"] = get_value(html.xpath("//h1[@id='xqtitle']"),'text','html')
    juzi_object["author"] = get_value(html.xpath("//div[@class='senconwriart']/span[1]/a[@rel='tag']"),'text')
    author_url= get_value(html.xpath("//div[@class='senconwriart']/span[1]/a[@rel='tag']"),'href')
    juzi_object["authorUrl"] = author_url
    next_url = get_value(html.xpath("//div[@class='nextlinks']/a[@class='goto-previous-node']"),'href')
    juzi_object["nextUrl"] = next_url

    text = json.dumps(juzi_object, ensure_ascii=False)
    with open('file/juzi/juzi_' + start + '.json', 'w', encoding='utf-8') as fs:
       fs.write(text)
    print('---------------存入句子数据:'+start + '------------------------------')
    time.sleep(4)
    if author_url.strip() != '':
        get_jzm_author(author_url)

    if next_url.strip() == '':
        print('---------------存入数据完成！！！------------------------------')
        return
    else:
        get_jzm_ju(next_url.replace('/ju/',''))


if __name__ == "__main__":
    urllib3.disable_warnings()
    get_jzm_ju('3')