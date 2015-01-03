#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import time
import urllib
import requests
from bs4 import BeautifulSoup
from pdb import set_trace as bp

def search(keywords, page=1):
    url = "http://www.torrentkitty.org/search/%s/%d" % \
        (keywords, page,)
    print >> sys.stderr, "下载 %s" % url
    response = requests.get(url, headers =
        { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 ' \
                         '(KHTML, like Gecko) Chrome/30.0.1599.101 ' \
                         'Safari/537.36' })


    c = response.text.encode("utf-8")
    s = BeautifulSoup(c)
    b = [i for i in
         s.
         find("table", {"id": "archiveResult"}).
         find_all("tr") if i.th == None]

    torrents = []
    for i in b:
        name = i.td.text
        size = i.find("td", {"class": "size"}).text
        upload_at = i.find("td", {"class": "date"}).text
        magnet = i.find("td", {"class": "action"}).a.next_sibling.attrs['href']
        
        torrent = {
            "name": name,
            "size": size,
            "upload_at": upload_at,
            "magnet": magnet
        }
        torrents.append(torrent)

    try:
        links = s.find("div", {"class": "pagination"}).find_all("a")
    except Exception, e:
        print e
        bp()
        sys.exit()
    next_link = links.pop()
    if next_link.has_attr('href'):
        next_link_index = int(next_link.attrs['href'])
    else:
        next_link_index = 0

    return torrents, next_link_index

DOWNLOAD_INTERVAL = 1
RETRY_INTERVAL = 10

def main():
    keywords = sys.argv[1]
    next_link_index = 1
    while True and next_link_index > 0:

        idx = 1
        while True:
            previous_next_link_index = next_link_index
            try:
                results, next_link_index = search(keywords, next_link_index)
                for result in results:

                    output = [i.encode("utf-8") for i in result.values()]
                    print >> sys.stdout, "\t".join(output)

                print >> sys.stderr, "第%d页，共%d条记录" % \
                    (previous_next_link_index, len(results))

                if next_link_index < previous_next_link_index:
                    print >> sys.stderr, "任务完成"
                    sys.exit()

                break
            except Exception, e:
                print >> sys.stderr, e
                dir(e)
                sys.exit()
                pass
            print >> sys.stderr, "第%d次重试" % idx
            idx += 1
            if idx > 10:
                print >> sys.stderr, "5次重试，放弃第%d页下载" % \
                    (previous_next_link_index)
                next_link_index += 1
                time.sleep(RETRY_INTERVAL)
        time.sleep(DOWNLOAD_INTERVAL)
if "__main__" == __name__:
    main()
