import os
import traceback
import re
import requests
import json
import time
from requests.packages import urllib3
from lxml import etree
import random
import urllib.request




# //h1/span 标题
# //img[@rel='v:photo'] 封面
# //div[@id='info'] 书籍 基本信息
# //div[@class='intro'] 书籍简介
# //div[@class='indent']/span/a 书籍标签
# //div[@id='interest_sectl'] 评分信息
# //div[@id='interest_sectl']//strong 平均评分
# //div[@id='interest_sectl']//span[@property] 人数
# //div[@id='interest_sectl']//span[@class='rating_per'] 评分占比
#
#
# //div[@class='mod-hd']/h2/span/a 短评链接
# https://book.douban.com/subject/30330291/comments/  书评 短评 新页面
# //li[@class='comment-item'] 评论list集合
# //li[@class='comment-item']/div/a/@href 评论用户地址
# //li[@class='comment-item']/div/a/img/@src 评论用户头像
# //li[@class='comment-item']/div[2]/h3/span[1]/span/text() 点赞
# //li[@class='comment-item']/div[2]/h3/span[2]/span/text() 评论时间
# //li[@class='comment-item']/div[2]/h3/span[2]/span[1]/@class 评论
# //li[@class='comment-item']/div[2]/p/span/text() 评论内容
#
#
# https://book.douban.com/subject/30330291/reviews 书评 长评论 新页面
# https://book.douban.com/review/9747117/
# //div[@data-cid] 评论list集合
# //div[@data-cid]/div/header/a/img/@src 评论人头像
# //div[@data-cid]/div/header/a[2]/text() 评论人姓名
# //div[@data-cid]/div/header/span[1]/@class 评论人 评分
# //div[@data-cid]/div/header/span[2]/text() 评论人 评论时间

# 
kv=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
{'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
{'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]
cookie ={"Cookie":''}
book_url = 'https://book.douban.com/subject/'


def requestWeb(url):
    # s.cookies.clear()
    # requests.utils.dict_from_cookiejar(resp.cookies)
    # resp.cookies.get_dict()
    time.sleep(random.randint(2,5))
    s = requests.session()

    if not cookie["Cookie"]:
        resp = s.get(url,verify=False,headers=kv[random.randint(0,2)])
        if len(resp.cookies.get_dict()) > 0:
            cookie["Cookie"] = 'bid=' + resp.cookies.get_dict()["bid"] +';viewed' + resp.cookies.get_dict()["viewed"] + ';'
    else:
        resp = s.get(url,verify=False,headers=kv[random.randint(0,2)],cookies=cookie)

    if resp.status_code == 403:
        s.cookies.clear()
        resp = s.get(url,verify=False,headers=kv[random.randint(0,2)])
        if len(resp.cookies.get_dict()) > 0:
            cookie["Cookie"] = 'bid=' + resp.cookies.get_dict()["bid"] +';viewed' + resp.cookies.get_dict()["viewed"] + ';'

    return resp


def get_value(items, str, type='text'):
    for i in items:
        try:
            if str == 'text':
                return (i.text if type == 'text' else etree.tostring(i, method='html', encoding="utf-8").decode('utf-8'))
            else:
                return i.attrib[str]
        except Exception as e:
            if not os.path.exists('douban/log/' + time.strftime("%Y-%m-%d") + '/'):
                os.makedirs('douban/log/' + time.strftime("%Y-%m-%d") + '/')
            with open('douban/log/' + time.strftime("%Y-%m-%d") + '/' + time.strftime("%H") + '.log', 'w', encoding='utf-8') as fs:
                fs.write('-------' + time.strftime("%H_%M_%S") + '----' + traceback.format_exc() +
                         '---:  (' + str + ')' + etree.tostring(i, method='html', encoding="utf-8").decode('utf-8'))
    return ''


def get_review_comment_detail(content, bcid):
    book_comment = {}
    html = etree.HTML(content, etree.HTMLParser())
    book_comment["comment_id"] = bcid
    book_comment["nick_name"] = get_value(
        html.xpath("//div[@class='header']/a"), 'text')
    book_comment["user_url"] = get_value(
        html.xpath("//div[@class='header']/a"), 'href')
    book_comment["head_image"] = get_value(html.xpath("//div[1]/a/img"), 'src')
    book_comment["comment_time"] = get_value(
        html.xpath("//div[@class='header']/span"), 'text')
    book_comment["content"] = get_value(html.xpath(
        "//p[@class='comment-text']"), 'text', 'html')
    return book_comment


def get_book_review_detail(review_url, brid, comment_total):
    book_review = {}
    req = requestWeb(review_url)
    html = etree.HTML(req.text, etree.HTMLParser())
    book_review["review_id"] = brid
    book_review["review_title"] = review_url
    book_review["review_title"] = get_value(
        html.xpath("//span[@property='v:summary']"), 'text')
    book_review["user_url"] = get_value(html.xpath(
        "//div[@class='article']/div/div/a"), 'href')
    book_review["head_image"] = get_value(html.xpath(
        "//div[@class='article']/div/div/a/img"), 'src')
    book_review["nick_name"] = get_value(html.xpath(
        "//header[@class='main-hd']/a/span"), 'text')
    book_review["review_score"] = get_value(html.xpath(
        "//header[@class='main-hd']/span[1]"), 'class')
    book_review["review_time"] = get_value(html.xpath(
        "//header[@class='main-hd']/span[3]"), 'text')
    book_review["review_content"] = get_value(
        html.xpath("//div[@class='main-bd']"), 'text', 'html')
    book_review["use_num"] = get_value(html.xpath("//button[1]"), 'text')
    book_review["nouse_num"] = get_value(html.xpath("//button[2]"), 'text')

    book_review["review_share"] = get_value(
        html.xpath("//span[@class='rec-num']"), 'text')
    book_review["review_reward"] = get_value(
        html.xpath("//span[@class='js-donate-count']"), 'text')
    book_review["review_comments"] = []

    if comment_total < 100:
        for i in html.xpath("//div[@class='comment-item']"):
            if i.text:
                book_review["review_comments"].append(get_review_comment_detail(etree.tostring(
                    i, method='html', encoding="utf-8").decode('utf-8'), i.attrib['data-cid']))
    else:
        for it in range(0, comment_total, 100):
            creq = requestWeb(review_url + '?start=' + str(it) + '#comments')
            chtml = etree.HTML(creq.text, etree.HTMLParser())
            for i in chtml.xpath("//div[@class='comment-item']"):
                if i.text:
                    book_review["review_comments"].append(get_review_comment_detail(etree.tostring(
                        i, method='html', encoding="utf-8").decode('utf-8'), i.attrib['data-cid']))

    return book_review


def get_book_comment_detail(content, bcid):
    book_comment = {}
    html = etree.HTML(content, etree.HTMLParser())
    book_comment["comment_id"] = bcid
    book_comment["nick_name"] = get_value(html.xpath("//div[1]/a"), 'title')
    book_comment["user_url"] = get_value(html.xpath("//div[1]/a"), 'href')
    book_comment["head_image"] = get_value(html.xpath("//div[1]/a/img"), 'src')
    book_comment["use_num"] = get_value(
        html.xpath("//div[2]/h3/span[1]/span"), 'text')
    book_comment["comment_score"] = get_value(
        html.xpath("//div[2]/h3/span[2]/span[1]"), 'class')
    book_comment["comment_time"] = get_value(
        html.xpath("//div[2]/h3/span[2]/span[2]"), 'text')
    book_comment["content"] = get_value(html.xpath(
        "//p[@class='comment-content']/span"), 'text', 'html')
    return book_comment


def get_book_annotation_detail(annotation_url, baid):
    book_annotation = {}
    req = requestWeb(annotation_url)
    html = etree.HTML(req.text, etree.HTMLParser())
    book_annotation["annotation_id"] = baid
    book_annotation["title"] = get_value(html.xpath("//h1"), 'text')
    book_annotation["nick_name"] = get_value(
        html.xpath("//div[@class='info']/h6/a"), 'text')
    book_annotation["user_description"] = get_value(
        html.xpath("//div[@class='info']/h6/span"), 'text')
    book_annotation["user_url"] = get_value(
        html.xpath("//div[@class='pic']/a"), 'href')
    book_annotation["head_image"] = get_value(
        html.xpath("//div[@class='pic']/a/img"), 'src')

    book_annotation["page_num"] = get_value(
        html.xpath("//span[@class='page-num']"), 'text')

    if book_annotation["page_num"] == '':
        book_annotation["page_num"] = get_value(html.xpath(
            "//div[@class='annotation-info']/ul/li[1]"), 'text')

    book_annotation["annotation_time"] = get_value(
        html.xpath("//span[@class='pubtime']"), 'text')
    book_annotation["annotation_content"] = get_value(
        html.xpath("//pre"), 'text', 'html')
    book_annotation["read_num"] = get_value(
        html.xpath("//div[@class='pl info']/span"), 'text')
    book_annotation["annotation_share"] = get_value(
        html.xpath("//span[@class='rec-num']"), 'text')

    return book_annotation


def get_book_comment(url, index, total):
    # /hot?p=1
    book_comments = []
    req = requestWeb(url + '/hot?p=' + str(index))
    html = etree.HTML(req.text, etree.HTMLParser())
    for i in html.xpath("//li[@class='comment-item']"):
        if i.text:
            book_comments.append(get_book_comment_detail(etree.tostring(
                i, method='html', encoding="utf-8").decode('utf-8'), i.attrib['data-cid']))
    if index <= total:
        book_comments.extend(get_book_comment(url, index+1, total))
    return book_comments


def get_book_reviews(url, index, total):
    # /?start=100#comments
    book_reviews = []
    req = requestWeb(url + '?start=' + str(index))
    html = etree.HTML(req.text, etree.HTMLParser())
    review_urls = html.xpath("//a[@class='reply ']")
    for i in review_urls:
        if i.attrib["href"] and i.text != '':
            brid = re.sub("\D", "", i.attrib["href"])
            comment_total = re.sub("\D", "", i.text)
            book_reviews.append(get_book_review_detail(
                i.attrib["href"], brid, int(comment_total)))
    if(index <= total):
        book_reviews.extend(get_book_reviews(url, index+20, total))
    return book_reviews


def get_book_annotations(url, index, total):
    # ?sort=rank&start=10
    book_annotations = []
    req = requestWeb(url + '?sort=rank&start=' + str(index))
    html = etree.HTML(req.text, etree.HTMLParser())
    review_urls = html.xpath("//h3/a")
    for i in review_urls:
        if i.attrib["href"] and i.text != '' and i.text is not None:
            baid = re.sub("\D", "", i.text)
            book_annotations.append(
                get_book_annotation_detail(i.attrib["href"], baid))

    if index <= total:
            book_annotations.extend(get_book_annotations(url, index+10, total))
    return book_annotations


def get_book(bid, b_url, dir, start):
    req = requestWeb(b_url)
    html = etree.HTML(req.text, etree.HTMLParser())
    book_object = {"url": b_url, "id": start}
    book_score = {}

    book_object["title"] = get_value(html.xpath('//h1/span'), 'text')
    book_object["cover"] = get_value(
        html.xpath("//img[@rel='v:photo']"), 'src')
    book_score["avg"] = get_value(html.xpath(
        "//div[@id='interest_sectl']//strong"), 'text')
    book_score["scroe_num"] = get_value(html.xpath(
        "//span[@property='v:votes']"), 'text')

    bases = html.xpath("//div[@id='info']//text()")
    base_str = ''
    for i in bases:
        format_i = i.replace('\n', '').replace(' ', '')
        if format_i:
            base_str = base_str + format_i
    book_object["base"] = base_str

    intros = html.xpath("//div[@class='intro']/p")
    intro_str = ''
    for i in intros:
        if i.text:
            intro_str = intro_str + i.text
    book_object["intro"] = intro_str

    tags = html.xpath("//div[@class='indent']/span/a")
    t = []
    for i in tags:
        if i.text:
            t.append(i.text)
    book_object["tags"] = t

    ratings = html.xpath(
        "//div[@id='interest_sectl']//span[@class='rating_per']")
    r = []
    for i in ratings:
        if i.text:
            r.append(i.text)

    book_score["rating"] = r
    book_object["score"] = book_score

    comment_page = get_value(html.xpath(
        "//div[@class='mod-hd']/h2/span[@class='pl']/a"), 'text')
    if comment_page != '':
        total = re.sub("\D", "", comment_page)
        book_object["comments"] = get_book_comment(
            b_url + 'comments', 1, (int(total) / 20) + 1)

    review_page = get_value(html.xpath("//header/h2/span/a"), 'text')
    if review_page != '':
        total = re.sub("\D", "", review_page)
        book_object["reviews"] = get_book_reviews(
            b_url + 'reviews', 0, int(total))

    annotation_page = get_value(html.xpath(
        "//span[@property='v:count']"), 'text')
    if annotation_page != '':
        total = re.sub("\D", "", annotation_page)
        book_object["annotations"] = get_book_annotations(
            b_url + 'annotation', 0, int(total))

    text = json.dumps(book_object, ensure_ascii=False)
    with open(dir + 'book_' + str(start) + '.json', 'w', encoding='utf-8') as fs:
       fs.write(text)
    print('---------------存入数据:'+str(start) + '------------------------------')


if __name__ == "__main__":
    urllib3.disable_warnings()
    dir = 'douban/file/book/'
    if not os.path.exists(dir):
        os.makedirs(dir)
        # 1000489
    for i in range(1000397, 30430801):
        url = book_url + str(i) + '/'
        get_book(i, url, dir, str(i))
        time.sleep(3)
