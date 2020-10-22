#!/usr/bin/env python
# coding: utf-8

#import pandas as pd
from lxml import html
import requests
from datetime import datetime
import logging
from pprint import pprint
import re

#HEADERS = {'User Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
#HEADERS = {'User Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36'}
HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
NEWS_SRC = ['https://news.mail.ru', 'https://lenta.ru/parts/news/', 'https://yandex.ru/news/']

logging.basicConfig(filename="parser.log",
                    format='%(asctime)s %(levelname)-5s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

response = requests.get(NEWS_SRC[1], headers=HEADERS)

print(response.status_code)

def get_mail_news(response):
    logging.info('Start parsing news.mail.ru')
    root = html.fromstring(response.text)
    news = root.xpath( '//div[contains(@class,"cols__inner")]' )
    news_list=[]
    for one_news in news:
        news_dict = {}
        news_dict['date'] = one_news.xpath('.//div[@class="newsitem__params"]/span/@datetime')[0]
        news_dict['news_agency'] = one_news.xpath('.//div[@class="newsitem__params"]/span[2]/text()')[0]
        news_dict['link'] = one_news.xpath('.//a[contains(@class,"newsitem__title")]/@href')[0]
        news_dict['title'] = one_news.xpath('.//a[contains(@class,"newsitem__title")]/span/text()')[0].replace('\xa0', ' ')
        news_list.append(news_dict)
    logging.info(f'Got {len(news_list)} news')
    return news_list

def get_yandex_news(response):
    logging.info('Start parsing news.yandex.ru')
    root = html.fromstring(response.text)
    news = root.xpath( '//article[contains(@class,"news-card")]' )
    news_list=[]
    for one_news in news:
        news_dict = {}
        news_dict['date'] = datetime.today().strftime('%Y-%m-%d') + ' ' + one_news.xpath('.//span[@class="mg-card-source__time"]/text()')[0]
        news_dict['news_agency'] = one_news.xpath('.//span[@class="mg-card-source__source"]/a/text()')[0]
        news_dict['link'] = one_news.xpath('.//a[contains(@class,"news-card__link")]/@href')[0]
        news_dict['title'] = one_news.xpath('.//h2[contains(@class,"news-card__title")]/text()')[0].replace('\xa0', ' ')
        news_list.append(news_dict)
    logging.info(f'Got {len(news_list)} news')
    pprint(news_list)
    return news_list

def get_lenta_news(response):
    logging.info('Start parsing lenta.ru')
    root = html.fromstring(response.text)
    news = root.xpath( '//div[contains(@class,"item news")]' )
    news_list=[]
    for one_news in news:
        news_dict = {}
        news_dict['date'] = datetime.today().strftime('%Y-%m-%d') + ' ' + one_news.xpath('.//div[@class="info g-date item__info"]/text()')[0]
        news_dict['news_agency'] = 'lenta.ru'
        news_dict['link'] = 'https://lenta.ru' + one_news.xpath('.//h3/a/@href')[0]
        news_dict['title'] = one_news.xpath('.//h3/a/text()')[0].replace('\xa0', ' ')
        news_list.append(news_dict)
    logging.info(f'Got {len(news_list)} news')
    pprint(news_list)
    return news_list

#get_mail_news(response)
#get_yandex_news(response)
get_lenta_news(response)
