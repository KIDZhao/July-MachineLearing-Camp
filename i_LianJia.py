# _*_ encoding:utf-8 _*_
__author__ = 'zhaoxu'
__date__ = '2017/4/9 9:25'
import codecs
import time
import sys
import re

import requests
from lxml import etree
from bs4 import BeautifulSoup
# from lxml.cssselect import CSSSelector
# import lxml.html
import csv

reload(sys)
sys.setdefaultencoding('utf8')


def spider_lj():
    s = requests.Session()
    url_lj = 'http://bj.lianjia.com/zufang/'
    url_location = ['dinghuisi', 'tiancun1', 'sijiqing', 'yuquanlu11', 'suzhouqiao', 'baishiqiao1', 'junbo1',
                    'liuliqiao1']
    num = 0
    info = []

    for where in url_location:
        url = url_lj + where + '/'
        r = s.get(url)
        r.encoding = 'utf-8'
        root = etree.HTML(r.content)
        # print r.content

        page_data = root.xpath('//@page-data')
        total_page = eval(str(page_data[0]))
        total_page = total_page.get('totalPage')

        for page in range(1, total_page + 1):
            url_page = url + str('pg%s/' % page)

            r_page = s.get(url_page)
            r_page.encoding = 'utf-8'
            root = etree.HTML(r_page.content)

            items = root.xpath('//*[@id="house-lst"]/li')
            for item in items:
                addr = item.xpath('div/div/div[@class="where"]/a/span/text()')[0].encode('gb2312', 'ignore').decode(
                    'gb2312')
                zone = item.xpath('div/div/div/span[@class="zone"]/span/text()')[0].encode('gb2312', 'ignore').decode(
                    'gb2312')
                meter = item.xpath('div/div/div/span[@class="meters"]/text()')[0].encode('gb2312', 'ignore').decode(
                    'gb2312')
                price = item.xpath('div/div/div[@class="price"]/span/text()')[0]
                floor = item.xpath('div/div/div[@class="other"]/div/text()')[0].encode('gb2312', 'ignore').decode(
                    'gb2312')
                year = item.xpath('div/div/div[@class="other"]/div/text()')[1].encode('gb2312', 'ignore').decode(
                    'gb2312')
                location = item.xpath('div/div/div[@class="other"]/div/a/text()')[0].encode('gb2312', 'ignore').decode(
                    'gb2312')
                url_apart = item.xpath('div[@class="info-panel"]/h2/a/@href')[0]
                num += 1
                info_pre = [location, addr, zone, meter, price, floor, year, url_apart]
                info.append(info_pre)
                print ('%d_%s: %s\t%s\t%s\t%s\t%s\t%s\t%s') % (
                    num, location, addr, zone, meter, price, floor, year, url_apart)

            time.sleep(1)

    return info


def spider_zr():
    s = requests.Session()
    Target = {u'定慧寺', u'马甸', u'苏州桥', u'五棵松', u'苏州桥', u'田村', u'玉泉路', u'军博', u'公主坟', u'白石桥'}
    # u'定慧寺', u'马甸', u'苏州桥', u'五棵松', u'苏州桥', u'田村', u'玉泉路', u'军博', u'公主坟', u'白石桥'
    target = {key: [] for key in Target}
    url = 'http://www.ziroom.com/z/nl/z2.html'  # z1= 自如整租 z2=友家合租 z3=自如月租
    # 伪造表头，防自如反爬
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
    r = s.get(url, headers=headers)
    content = r.content
    soup = BeautifulSoup(content, 'html5lib')
    content = soup.prettify()
    root = etree.HTML(content)
    info = []  # 记录爬取信息
    # 获取目标区域URL地址
    items = root.xpath('//*[@id="selection"]/div/div/dl[2]/dd/ul/li[5]/div/span')
    print "地区标签总数:", len(items)
    for i, item in enumerate(items):
        tag = item.xpath('a/text()')[0].strip().encode('gb2312', 'ignore').decode('gb2312')
        url_tag = item.xpath('a/@href')[0].split("//")[-1]
        if target.has_key(tag):
            target[tag] = 'http://' + url_tag

    num = 0  # 记录编号
    for url_aim in target:
        print target[url_aim], ":", url_aim
        r = s.get(target[url_aim], headers=headers)
        r.encoding = 'utf-8'
        content = r.content
        soup = BeautifulSoup(content, 'html5lib')
        content = soup.prettify()
        root = etree.HTML(content)

        # pages = 1
        try:
            pages = root.xpath('//*[@id="page"]/span[1]/text()')[0].strip()
            # 共4页
            m = re.findall(r'([0-9]+)', pages)
            pages = int(m[0])
        except:
            pages = 1

        for page in range(1, pages + 1):  # 此处首页会加载两遍，有待优化
            url_page = target[url_aim] + '?p=%d' % page
            print url_page, url_aim
            r = s.get(url_page, headers=headers)
            r.encoding = 'utf-8'
            content = r.content
            soup = BeautifulSoup(content, 'html5lib')
            content = soup.prettify()
            root = etree.HTML(content)

            items = root.xpath('//*[@id="houseList"]/li')  # 获取所有租房项内容
            for item in items:
                addr = item.xpath('div[2]/h3/a/text()')[0].strip().split('-')[0][:-3].encode('gb2312', 'ignore').decode('gb2312')
                # zone = item.xpath('div[2]/h3/a/text()')[0].strip().split('-')[0][-3:].encode('gb2312', 'ignore').decode('gb2312')
                direc = item.xpath('div[2]/h3/a/text()')[0].strip().split('-')[1].encode('gb2312', 'ignore').decode('gb2312')
                url_apart = 'http:' + item.xpath('div[2]/h3/a/@href')[0]
                location = item.xpath('div[2]/h4/a/text()')[0].strip().split(']')[0][1:].encode('gb2312', 'ignore').decode(
                    'gb2312')
                meter = item.xpath('div[2]/div/p[1]/span[1]/text()')[0].strip().encode('gb2312', 'ignore').decode(
                    'gb2312').strip()
                floor = item.xpath('div[2]/div/p[1]/span[2]/text()')[0].strip().encode('gb2312', 'ignore').decode('gb2312')
                zone = item.xpath('div[2]/div/p[1]/span[3]/text()')[0].strip().encode('gb2312', 'ignore').decode('gb2312')
                price = item.xpath('div[3]/p[@class="price"]/text()')[0].strip().encode('gb2312', 'ignore').decode('gb2312')[2:]
                num += 1
                info_pre = [location, addr, zone, direc, meter, price, floor, url_apart]
                info.append(info_pre)
                print num, ":", location, addr, zone, direc, meter, price, floor, url_apart
            time.sleep(1)
    return info


def spider_58():
    s = requests.Session()
    url_58 = 'http://bj.58.com/'
    url_key = ['dinghuisi', 'tiancunlu', 'sijiqinghd', 'bjyql', 'suzhouqiao', 'beiwalu', 'hangtianqiao', 'huayuanqiao',
               'suzhoujie', 'junbo']
    # , 'tiancunlu', 'sijiqinghd', 'bjyql', 'suzhouqiao', 'beiwalu', 'hangtianqiao', 'huayuanqiao','suzhoujie', 'junbo'
    url_val = [u'定慧寺', u'田村', u'四季青', u'玉泉路', u'苏州桥', u'北洼路', u'航天桥', u'花园桥', u'苏州街', u'军博']
    # , u'田村', u'四季青', u'玉泉路', u'苏州桥', u'北洼路', u'航天桥', u'花园桥',u'苏州街',u'军博'
    url_location = dict(zip(url_key, url_val))
    num = 0
    num_failure = 0
    info = []
    for where in url_location:
        url = url_58 + where + '/hezu/'
        # print url
        page = 0
        while (url is not None):
            r = s.get(url)
            r.encoding = 'utf-8'
            root = etree.HTML(r.content)
            try:
                items = root.xpath('/html/body/div[3]/div[1]/div[5]/div[2]/ul[@class="listUl"]/li')
                for item in items:
                    try:
                        # location = item.xpath('div[2]/p[2]/a[1]/text()')[0].strip().encode('gb2312', 'ignore').decode('gb2312')
                        # location_data = item.xpath('div[2]/p[@class="add"]')
                        # location = location_data.xpath('string(.)').extract()[0]
                        location = url_location[where]
                        # addr = item.xpath('div[2]/p[2]/a[2]/text()')[0].strip().encode('gb2312', 'ignore').decode('gb2312')
                        # lstr = re.findall('\w+', item.xpath('div[2]/p[@class="room"]/text()')[0])
                        # zone = '%s居室' % lstr[0]
                        # meter = lstr[1]
                        lstr = ''.join(item.xpath('div[2]/p[@class="room"]/text()')[0]).replace(u'\xa0', u' ').split(' ')
                        '/div[2]/p[1]'
                        zone = lstr[0]
                        meter = lstr[-1][:-1]
                        try:
                            source = item.xpath('div[2]/p[@class="geren"]/span/text()')[0].strip().encode(
                                'gb2312', 'ignore').decode('gb2312')[2:-1]
                        except:
                            source = item.xpath('div[2]/div[@class="jjr"]/text()')[0].strip().encode(
                                'gb2312', 'ignore').decode('gb2312')[2:-1]
                        price = item.xpath('div[3]/div[2]/b/text()')[0]
                        decs = item.xpath('div[2]/h2/a/text()')[0].strip().encode('gb2312', 'ignore').decode('gb2312')
                        url_apart = item.xpath('div[2]/h2/a/@href')[0]
                        # location = item.xpath('div[2]/p[2]/a[1]/text()')
                        # '/html/body/div[3]/div[1]/div[5]/div[2]/ul/li[1]/div[2]/p[2]/a[2]'
                        # info_pre = [location, addr, zone, direc, meter, price, floor, url_apart]
                        num += 1
                        info_pre = [location, zone, meter, source, price, url_apart, decs]
                        info.append(info_pre)
                        print num, ":", location, zone, meter, source, price, url_apart, decs
                    except Exception as e:
                        num_failure += 1
                        print "Failure:", num_failure, ":", e

                page += 1
                url = root.xpath('//*[@id="bottom_ad_li"]/div[2]/a[@class="next"]/@href')[0]
                print page, ":", url
                time.sleep(2)
            except:
                url = None
    return info


def writeResult(filename, info, type):
    filename = str('SpiderData/%s.csv' % filename)
    with open(filename, 'wb') as csvfile:
        csvfile.write(codecs.BOM_UTF8)
        resultData = csv.writer(csvfile)
        if type == 'LJ':
            resultData.writerow([u'区域', u'地址', u'户型', u'面积', u'价格', u'楼层', u'建造时间', u'链接地址'])
        elif type == 'ZR':
            resultData.writerow([u'区域', u'地址', u'户型', u'朝向', u'面积', u'价格', u'楼层', u'链接地址'])
        elif type == '58':
            resultData.writerow([u'区域', u'户型', u'面积', u'房源', u'价格', u'链接', u'描述'])
        else:
            return False
        for item in info:
            resultData.writerow(item)


if __name__ == "__main__":
    writeResult('LJdata', spider_lj(), 'LJ')
    # writeResult('ZRdata', spider_zr(), 'ZR')
    # writeResult('58data', spider_58(), '58')
