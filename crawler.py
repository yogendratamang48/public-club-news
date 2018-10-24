import random
import ast

USER_AGENTS_FILE = 'useragents.txt'
PROXIES_FILE = 'proxies.txt'

USER_AGENTS = ast.literal_eval(open(USER_AGENTS_FILE).read())
PROXIES = ast.literal_eval(open(PROXIES_FILE).read())

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
