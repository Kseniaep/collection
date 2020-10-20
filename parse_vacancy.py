#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import logging
from pprint import pprint
import re
import datetime

URL_SUPERJOB = 'https://www.superjob.ru'
URL_HH = 'https://hh.ru'
# HEADERS = {'User Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
SAVE_PATH = './data'


logging.basicConfig(filename="parser.log",
                    format='%(asctime)s %(levelname)-5s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')




def salary_split_sj(salary):
    """
    Parse salary string for SuperJob on fields from, to, currency, period
    """
    salary_dict = {}
    
    salary = salary.replace(' ','')

    if salary == 'Подоговорённости':
        return salary_dict
    else:
        currency_match = re.search('\d+(?P<cur>\D+)/(?P<period>.+)', salary)
        if currency_match:
            salary_dict['currency'] = currency_match.group('cur')
            salary_dict['period'] = currency_match.group('period')
        else:
            raise ValueError (f'Can`t match currency value in string:\n{salary}')

        salary_match = re.search('^от(?P<from>\d{1,7})', salary)
        if salary_match:
            salary_dict['from'] = int(salary_match.group('from'))
            return salary_dict

        salary_match = re.search('^до(?P<to>\d{1,7})', salary)
        if salary_match:
            salary_dict['to'] = int(salary_match.group('to'))
            return salary_dict

        salary_match = re.search('(?P<from>\d{1,7})—(?P<to>\d{1,7})', salary)
        if salary_match:
            salary_dict['from'] = int(salary_match.group('from').replace(' ', ''))
            salary_dict['to'] = int(salary_match.group('to').replace(' ', ''))
            return salary_dict

        salary_match = re.search('^(?P<eq>\d{1,7})', salary)
        if salary_match:
            salary_dict['from'] = int(salary_match.group('eq').replace(' ', ''))
            salary_dict['to'] = salary_dict['from'] 
            return salary_dict

        raise ValueError (f'Can`t match salary value in string:\n{salary}')

    return salary_dict

def salary_split_hh(salary):
    """
    Parse salary string for HH on fields from, to, currency, period
    """
    salary_dict = {}

    salary = salary.replace('-', ' ')
    salary = salary.replace('.', '')
    if salary == 'По договорённости':
        return salary_dict
    else:
        salary_sp = salary.split(' ')
        salary_dict['currency'] = salary_sp[-1]
        if salary_sp[0] == 'от':
            salary_dict ['from'] = salary_sp[1]
        elif salary_sp[0] == 'до':
            salary_dict['to'] = salary_sp[1]
        elif salary_sp[0].isdigit():
            salary_dict['from'] = salary_sp[0]
            salary_dict['to'] = salary_sp[1]
        return salary_dict

def parse_page_sj(url, keywords, page):
    """
    Return name, link and salary from SuperJob page for keywords search word
    """
    params = {'keywords': keywords, 'page':page}
    response = requests.get(url, params=params, headers=HEADERS)
    soup = bs(response.text, "html.parser")
    tags_div = soup.find_all('div', attrs={'class':'f-test-vacancy-item'})
    vacancies =[]
    for tag_div in tags_div:
        vacancy =  {}
        caption = tag_div.findChild(recursive=False).find('a')
        if caption:
            vacancy['name'] = caption.get_text()
            vacancy['link'] = URL_SUPERJOB + caption['href']
        salary = tag_div.find_all('span', {'class':'f-test-text-company-item-salary'})[0].text.replace(u'\xa0', u' ')

        logging.debug(f'Parsing salary string {salary}')
        salary_dict = salary_split_sj(salary)
        logging.debug(f'Result fields {salary_dict}')

        vacancy.update(salary_dict)

        vacancies.append(vacancy)
    next_page = soup.find_all('a', attrs={'rel':'next'})
    return vacancies, next_page

def parse_page_hh(url, keywords, page):
    """
    Return name, link and salary from HH page for keywords search word
    """
    params = {'text': keywords, 'page':page}
    response = requests.get(url, params=params, headers=HEADERS)
    soup = bs(response.text, "html.parser")
    tags_div = soup.find_all('div', attrs={'class': 'vacancy-serp-item__row vacancy-serp-item__row_header'})
    vacancies =[]
    for tag_div in tags_div:
        vacancy = {}
        caption = tag_div.findChild(recursive=False).find('a')
        if caption:
            vacancy['name'] = caption.get_text()
            vacancy['link'] = caption['href']
        salary = tag_div.find_all('div', {'class': 'vacancy-serp-item__sidebar'})
        if salary:
            salary = salary[0].get_text().replace(u'\xa0',u'')
        vacancy.update(salary_split_hh(salary))
        vacancies.append(vacancy)

    next_page = soup.find_all('a', attrs={'class':'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
    return vacancies, next_page

def get_sj(keywords):
    """
    Create DataFrame for SuperJob
    """
    url = URL_SUPERJOB + '/vacancy/search/'

    next_exist = True
    page = 1
    vacancys = []
    logging.info('SJ parsing started')
    while next_exist:
        logging.debug(f'page={page}')
        vacancys_page, next_page = parse_page_sj(url, keywords, page)
        vacancys.extend(vacancys_page)
        page += 1
        if next_page:
            pass
        else:
            logging.info('Last page reached')
            next_exist = False

    df = pd.DataFrame(vacancys)

    df['source'] = 'SJ'
    logging.info(f'From SJ recived {len(df)} vacancies for {keywords}')
    return df



def get_hh(keywords):
    """
    Create DataFrame for HH
    """
    url = URL_HH + '/search/vacancy'

    next_exist = True
    page = 1
    vacancys = []
    logging.info('HH parsing started')
    while next_exist:
        logging.debug(f'page={page}')
        vacancys_page, next_page = parse_page_hh(url, keywords, page)
        vacancys.extend(vacancys_page)
        page += 1
        if next_page:
            pass
        else:
            logging.info('Last page reached')
            next_exist = False

    df = pd.DataFrame(vacancys)

    df['source'] = 'HH'
    df['period'] = 'месяц'
    logging.info(f'From HH recieved {len(df)} vacancies for {keywords}')
    return df


def write_vacancies(keyword):
    """
    Create parsing file, print data
    """
    logging.info('Start fetching data')
    now = datetime.datetime.now()
    date_sufix = now.strftime('%Y-%m-%d_%H-%m-%S')
    file_name = SAVE_PATH + '/' + keyword+date_sufix+'.pkl'

    df_sj = get_sj(keyword)
    print(f'Got {len(df_sj)} vacancies from SJ')
    df_hh = get_hh(keyword)
    print(f'Got {len(df_hh)} vacancies from HH')
    df = pd.concat([df_sj,df_hh],ignore_index = True)
    logging.info('Data recived')

    df.to_pickle(file_name)
    logging.info(f'Data saved to {file_name}')
    print(f'Got {len(df)} vacancies for {keyword}')
    pd.set_option('display.max_columns',None)
    print(df)
    return 1


keyword = 'строитель'
write_vacancies(keyword)



