#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests, re
from pyquery import PyQuery

url = 'http://***.com/budongsajiaodenvren/'

req = requests.get(url)

html = req.text
pq = PyQuery(html)
locatedDIV = pq('div#con_one_1')

regex = r"[\u4e00-\u9fa5]\d+[\u4e00-\u9fa5]\$\w+:\/\/pan.baidu.com\/s\/\w+\s[\u4e00-\u9fa5]{2}[\uff1a]\w{4}"

target = locatedDIV.text()
div = target.encode('latin-1').decode('gb2312')

re_words = re.compile(regex)
matches = re.findall(re_words, div)

for item in matches:
    item = item.split('$')
    title = item[0]
    item2 = item[1].split(' 密码：')
    url = item2[0]
    password = item2[1]

    print(title, url, password)
