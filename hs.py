__author__ = 'KentChum'
# -*- coding:utf-8 -*-
import tornado.httpclient
import json
import pymongo
import time
import urllib2

mapp = {
    'hot': '0',
}

conn = pymongo.MongoClient()
db = conn.hsvideo_bk

httpclient = tornado.httpclient.HTTPClient()


def datetime_timestamp(dt, fmt):
    s = time.mktime(time.strptime(dt, fmt))
    return int(s)


def get_json(url):
    res = httpclient.fetch(url)
    print url
    return json.loads(res.body)


def len_m3u8(url):
    if not url.endswith('m3u8'):
        return 500
    try:
        res = httpclient.fetch(url)
    except tornado.httpclient.HTTPError:
        return 0
    ret = 0
    for r in res.body.split('\n'):
        if r.startswith('#EXTINF'):
            ll = r.split(':')[1].split(',')[0]
            ret += float(ll)
    return int(ret)


def fetch_1006(clear=False):
    print '1006'
    if clear:
        db.tv1006.albums.drop()
        db.tv1006.videos.drop()

    tpl = 'http://v.iphone.1006.tv/mainpage2/lscsvideo/?channel=1'
    res = get_json(tpl)

    #print res
    for r in res['result']:
        if db.tv1006.albums.find_one({'_id': r['id']}):
            continue
        r['_id'] = r['id']
        lst = r['list']
        del r['list']
        db.tv1006.albums.save(r)
        db.tv1006.albums.ensure_index('cate', 1)
        for rr in lst:
            if db.tv1006.videos.find_one({'_id': rr['id']}):
                continue
            rr['album_id'] = r['id']
            rr['_id'] = rr['id']
            print rr['video_addr']
            if 'm3u8' not in rr['video_addr']:
                rr['length'] = 500
            else:
                rr['length'] = len_m3u8(rr['video_addr'])
            rr['published'] = int(rr['vtime'])
            db.tv1006.videos.save(rr)
            db.tv1006.videos.ensure_index('album_id', 1)


def fetch_17173(clear=False):
    print '17173'
    if clear:
        db.hs17173.albums.drop()
        db.hs17173.videos.drop()

    mapp = [245031, 244775, 241295]
    for m in mapp:

        payload = """{"input": {"page": 1,"size": 30,"appId": 3,"deviceType": 1,"newsKind": %d}}""" % int(m)
        url = 'http://m.app.shouyou.com/video/listVideo.json'

        data = ''
        fails = 0
        while True:
            try:
                if fails >= 20:
                    break
                result = urllib2.urlopen(url, data=payload, timeout=10)
                data = json.loads(result.read())

            except:
                fails += 1
                print 'network had some troubles,try it again.', fails

            else:
                break

        mapp_dict = {245031: r'娱乐视频', 244775: r'对战视频', 241295: r'解说视频'}

        album = {'id': m, 'album_name': mapp_dict[m]}
        #print album
        if db.hs17173.albums.find_one({'album_name': mapp_dict[m]}) is None:
            db.hs17173.albums.insert(album)

        for r in data['data']['newsList']:
            #print data
            r['album_id'] = m
            #r['_id'] = r['newsId']
            if db.hs17173.videos.find_one({'id': r['newsId']}) is None:
                db.hs17173.videos.insert(r)

    print 'finished'


def get_data_by_urllib2(url, payload=''):
    fails = 0
    while True:
        try:
            if fails >= 20:
                break
            result = urllib2.urlopen(url, data=payload, timeout=10)
            data = json.loads(result.read())

        except:
            fails += 1
            print 'network had some troubles,try it again.', fails
            data = ''

        else:
            break

    return data


fetch_1006()
fetch_17173()