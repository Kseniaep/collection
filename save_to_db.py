#!/usr/bin/env python
# coding: utf-8

from pprint import pprint
import pandas as pd
from pymongo import MongoClient
from glob import glob

LOAD_PATH = './data'

client = MongoClient('localhost', 27017)
db = client.vacancies


def load_all_data (path):
    """
    Load parsed data from df in pickles to Mongodb
    """
    data_files = glob(LOAD_PATH + '/*.pkl')
    print(data_files)
    for file in data_files:
        df = pd.read_pickle(file)
        if len(df)>0:
            db.vacancy.insert_many(df.to_dict('records'))


def load_new_data(path):
    """
    Load parsed data from df in pickles to Mongodb
    """
    data_files = glob(path + '/*.pkl')
    print(data_files)
    for file in data_files:
        counter = 0
        df = pd.read_pickle(file)
        if len(df)>0:
            for row in df.to_dict('records'):
                filter = {'name': row['name'],
                          'link': row['link'],
                          'from': row['from'],
                          'to': row['to'],
                          'currency': row['currency']}

                if db.vacancy.count_documents(filter=filter) == 0:
                    db.vacancy.insert_one(row)
                    counter += 1
        print(f'Loaded from {file} {counter} new vacancies.')

def print_salary_gte (salary, include_without_salary=False, currency='руб'):
    """
    Find documents with salary greater or equal salary
    """
    if include_without_salary:
        filter = { "$and": [ { "$or" : [ { "from" : { "$lte": salary } }, { "from": float('nan')}] },\
                                                {"$or":[{"to": {"$gte": salary}},{"to": float('nan')}]}]}
    else:
        filter = {"$and": [{"$or": [{"from": {"$lte": salary}}]}, \
                           {"$or": [{"to": {"$gte": salary}}]},
                           {'currency': currency}]}
    find_res = db.vacancy.find(filter,{'name': 1, 'from': 1, 'to': 1, '_id': 0})

    for rec in find_res:
        pprint(f'{rec["name"]} {rec["from"]} {rec["to"]}')

    print(f'Total vacancies with salary >= {salary}: {db.vacancy.count_documents(filter=filter)}')


path = LOAD_PATH
load_new_data(path)

print_salary_gte(60000)


# db.vacancy.delete_many({})








