#import requests
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

#import time

class Trails(object):
    def __init__(self):
        url = "https://www.trianglemtb.com/"
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        req = Request(url, headers={'User-Agent': user_agent})
        response = urlopen(req).read()
        print (response)
        soup = BeautifulSoup(response)
        
        