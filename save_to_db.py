#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
from pprint import pprint
import pandas as pd
from pymongo import MongoClient
from glob import glob

LOAD_PATH = './check'

client = MongoClient('localhost', 27017)
db = client.vacancies

# load parsing data
data_files = glob(LOAD_PATH + '/*.pkl')

for file in data_files:
    df = pd.read_pickle(file)
    if len(df)>0:
        db.vacancy.insert_many(df.to_dict('records'))

""" Check salary 60 000"""
find_res = db.vacancy.find({ "$and" : [ { "$or" : [ { "from" : { "$lte" : 60000 } }, { "from" : None } ] }, {"$or":[{"to":{"$gte" :60000}},{"to":None}]}]})

for rec in find_res:
    pprint(rec)

db.vacancy.count_documents({})

#db.vacancy.delete_many({})

#df.info()







