#!/usr/bin/env python
# coding: utf-8

from lxml import html
import requests
import logging
from datetime import datetime
from pymongo import MongoClient

HEADERS = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

logging.basicConfig(filename="parser.log",
                    format='%(asctime)s %(levelname)-5s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

client = MongoClient('localhost', 27017)
db = client.news


def get_request(url):
    response = requests.get(url, headers=HEADERS)
    if str(response.status_code)[0] == '2':
        return response
    else:
        raise Exception (f'Code {response.status_code}')

def get_mail_news():
    NEWS_SRC = 'https://news.mail.ru'
    logging.debug(f'Start parsing {NEWS_SRC}')
    try:
        response = get_request(NEWS_SRC)
    except Exception:
        raise ValueError("Can't get news.")
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
    logging.debug(f'Got {len(news_list)} news')
    return news_list

def get_yandex_news():
    NEWS_SRC = 'https://yandex.ru/news/'
    logging.debug(f'Start parsing {NEWS_SRC}')
    try:
        response = get_request(NEWS_SRC)
    except Exception:
        raise ValueError("Can't get news.")
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
    logging.debug(f'Got {len(news_list)} news')
    return news_list


def get_lenta_news():
    NEWS_SRC = 'https://lenta.ru/parts/news/'
    logging.debug(f'Start parsing {NEWS_SRC}')
    try:
        response = get_request(NEWS_SRC)
    except Exception:
        raise ValueError("Can't get web page.")
    root = html.fromstring(response.text)
    news = root.xpath( '//div[contains(@class,"item news")]' )
    news_list=[]
    for one_news in news:
        news_dict = {}
        news_dict['date'] = datetime.today().strftime('%Y-%m-%d') + ' ' + one_news.xpath('.//div[@class="info g-date item__info"]/text()')[0]
        news_dict['news_agency'] = 'lenta.ru'
        news_dict['link'] = one_news.xpath('.//h3/a/@href')[0]
        news_dict['title'] = one_news.xpath('.//h3/a/text()')[0].replace('\xa0', ' ')
        news_list.append(news_dict)
    logging.debug(f'Got {len(news_list)} news')
    return news_list

def load_new_data(records):
    """
    Load news to Mongodb
    """
    counter = 0
    for record in records:
        filter = {'date': record['date'],
                  'news_agency': record['news_agency'],
                  'link': record['link'],
                  'title': record['title']
                 }
        if db.news.count_documents(filter=filter) == 0:
            db.news.insert_one(record)
            counter += 1
    print(f'Loaded {counter} news.')

def get_and_load_all():
    mail_news = get_mail_news()
    load_new_data(mail_news)

    lenta_news = get_lenta_news()
    load_new_data(lenta_news)

    yandex_news = get_yandex_news()
    load_new_data(yandex_news)

get_and_load_all()

for rec in db.news.find({},{'title': 1, '_id': 0}):
    print(rec['title'])

# db.news.delete_many({})

