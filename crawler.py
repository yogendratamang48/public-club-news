#! /usr/bin/env python
'''
crawler.py - a minimal crawler script to club data from
https://www.newsnow.co.uk/h/Sport/Football/Championship/Blackburn+Rovers

Things to do:
1. Randomize useragents (or go with fake_user_agent
2. Remove those with `Gallery` heading
3. Randomize or use proxy in `get_random_proxy` method
4. Cron service to run the crawler in every hour or so
5. With increase in club links, one should move to asynchronous mode,
6. Async can be done either with `scrapy` or `celery` with `rabbitmq`
7. Code is already modular so we only need modify request part
8. Application will be scalable if there is database and parse_page
implements that more effectively
'''
import argparse
import os
import requests
import pandas as pd
from lxml import html


AP = argparse.ArgumentParser()
AP.add_argument("-d", "--debug", required=False,
                help="start in debug mode")


ARGS = vars(AP.parse_args())

if ARGS['debug']:
    import pudb
    pudb.set_trace()

if not os.path.exists('data'):
    os.mkdir('data')

CONFIG = {
    'results': '//div[@class="hl "]',
    'final_url': '//div[@id="retrieval-msg"]//a/@href',
    'fields': {
        'flag': ['//span[1]/@c'],
        'headline': ['//div[@class="hl__inner"]/a/text()'],
        'raw_link': ['//div[@class="hl__inner"]/a/@href'],
        'raw_source': ['//span[@class="src"]/@data-pub'],
        'source': ['//span[@class="src"]/span/text()'],
        'timestamp': ['//span[@class="time"]/@data-time'],
        'time': ['//span[@class="time"]/text()'],
    }
}


def extract_url(url):
    ''' gets final url '''
    try:
        print("Working in %s" % url)
    except:
        pass
    resp_content = get_page_html(url)
    page = html.fromstring(resp_content)
    _url = page.xpath(CONFIG['final_url'])
    if _url:
        return _url[0]
    return None


def get_club_url():
    ''' returns list of dictionary of form {'name':'', 'url':''}

    To Work:
    Maintain a list file, say, club_links.txt which will
    list all club with their urls
    '''

    url = 'https://www.newsnow.co.uk/h/Sport/Football/'\
        'Championship/Blackburn+Rovers'
    club = {'name': 'black_robers', 'url': url}
    clubs = []
    clubs.append(club)
    return clubs


def fetch_data(_res_sel):
    '''
    extracts dict data from single row
    '''
    head = {}
    for key, value in CONFIG['fields'].items():
        for _item in value:
            head[key] = None
            x_val = _res_sel.xpath(_item)
            if x_val:
                head[key] = x_val[0].strip()
                break
    head['final_url'] = extract_url(head['raw_link'])
    return head


def get_random_header():
    '''
    return random useragent header

    Todo:
    Maintain list of useragents, say useragents.py and
    read them randomly
    '''
    header = {}
    header['USER-AGENT'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64;"\
        " rv:57.0) Gecko/20100101 Firefox/57.0"
    return header


def get_random_proxy():
    '''
    returns random  proxy from list of proxies
    To do:
        maintain list of proxies or use other service like proxymesh
    '''
    random_proxy = {}
    random_ip_port = '192.168.1.113:8080'
    random_proxy['http'] = 'http://'+random_ip_port
    random_proxy['https'] = 'http://'+random_ip_port
    return random_proxy


def get_page_html(url):
    '''
    reads html from a give link

    This is separated to make this scalable in future
    '''
    headers = get_random_header()
    resp = requests.get(url, headers=headers)
    return resp.content


def parse_page(club):
    '''
    finds club url
    '''
    print("Working on Club: %s" % club.get('name'))
    url = club.get('url')
    resp_content = get_page_html(url)
    page = html.fromstring(resp_content)
    results = page.xpath(CONFIG['results'])
    results_sel = [html.fromstring(html.tostring(_res)) for _res in results]
    headlines = []
    for _sel in results_sel:
        _headline = fetch_data(_sel)
        headlines.append(_headline)
    df_headlines = pd.DataFrame(headlines)
    print("Saving to CSV:")
    file_name = 'data/' + club.get('name') + '.csv'
    df_headlines.to_csv(file_name, encoding='utf-8')


if __name__ == '__main__':
    ''' main '''
    clubs = get_club_url()
    for club in clubs:
        parse_page(club)
