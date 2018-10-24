import requests
import random
import ast
import pandas as pd
import argparse
import os
from lxml import html


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--debug", required=False,
	help="start in debug mode")

USER_AGENTS_FILE = 'useragents.txt'
PROXIES_FILE = 'proxies.txt'

USER_AGENTS = ast.literal_eval(open(USER_AGENTS_FILE).read())
PROXIES = ast.literal_eval(open(PROXIES_FILE).read())

args = vars(ap.parse_args())

if args['debug'] is not None:
    import pudb
    pudb.set_trace()

if not os.path.exists('data'):
    os.mkdir('data')

CONFIG = {
    'results':'//div[@class="hl "]',
    'final_url':'//div[@id="retrieval-msg"]//a/@href',
    'fields':{
        'flag':['//span[1]/@c'],
        'headline':['//div[@class="hl__inner"]/a/text()'],
        'raw_link':['//div[@class="hl__inner"]/a/@href'],
        'raw_source':['//span[@class="src"]/@data-pub'],
        'source':['//span[@class="src"]/span/text()'],
        'timestamp':['//span[@class="time"]/@data-time'],
        'time':['//span[@class="time"]/text()'],
    }


}

def extract_url(url):
    ''' gets final url '''
    try:
        print("Working in %s" % url)
    except:
        pass
    header = get_random_header()
    resp = requests.get(url, headers=header)
    page = html.fromstring(resp.content)
    _url = page.xpath(CONFIG['final_url'])
    if len(_url)>0:
        return _url[0]
    return None

def get_club_url():
    ''' returns list of dictionary of form {'club':'', 'url':''} '''
    raw_clubs = open('club_links.txt').read()
    raw_clubs = raw_clubs.split('\n')
    raw_clubs = [_c for _c in raw_clubs if _c.strip()!='']
    clubs = [{'name':_c.split('$')[-1], 'url':_c.split('$')[0]} for _c in raw_clubs]
    return clubs

    
def fetch_data(_res_sel):
    '''
    extracts dict data from single row
    '''
    head = {}
    for key,value in CONFIG['fields'].items():
       for _item in value:
           head[key] = None
           x_val = _res_sel.xpath(_item)
           if len(x_val)>0:
               head[key] = x_val[0].strip()
               break
    head['final_url'] = extract_url(head['raw_link'])
    return head

def get_random_proxy():
    '''
    returns random single proxy
    '''
    random_proxy = {}
    random_ip_port = PROXIES[random.randint(0, len(PROXIES)-1)]
    random_proxy['http'] = 'http://'+random_ip_port
    random_proxy['https'] = 'http://'+random_ip_port
    return random_proxy


def get_random_header():
    '''
    return headers with random useragent
    '''
    header = {}
    random_digit = random.randint(0, len(USER_AGENTS)-1)
    header['User-Agent'] =  USER_AGENTS[random_digit]
    return header

def parse_page(club):
    ''' parses club url '''
    print("Working on Club: %s" % club.get('name'))
    header = get_random_header()
    resp = requests.get(club.get('url'), headers=header)
    page = html.fromstring(resp.content)
    results = page.xpath(CONFIG['results'])
    results_sel = [html.fromstring(html.tostring(_res)) for _res in results]
    headlines = []
    for _sel in results_sel:
        _headline = fetch_data(_sel)
        headlines.append(_headline)
    df = pd.DataFrame(headlines)
    print("Saving to CSV:")
    file_name = 'data/' + club.get('name') + '.csv'
    df.to_csv(file_name, encoding='utf-8')

if __name__=='__main__':
    ''' main '''
    clubs = get_club_url()
    for club in clubs:
        parse_page(club)
