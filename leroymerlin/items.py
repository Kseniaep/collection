# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags

def correct_url(value):
    value = value.replace('/m/','/b/')
    return value

def correct_price(value: str):
    value = ''.join([x for x in value if x.isdigit()])
    value = int(value)
    return value

def correct_spec(value: list):
    value = value.split('\n')
    value = map(lambda x: x.strip(), value)
    # Remove empty
    value = [x for x in value if len(x) > 0]
    # Creating list containing keys alone by slicing
    keys = value[::2]
    # Creating list containing values alone by slicing
    values = value[1::2]
    # merging two lists uisng zip()
    z = zip(keys, values)
    # Converting zip object to dict using dict() constructor.
    spec_dict = dict(z)
    return spec_dict

class leroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(correct_price), output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose())
    spec = scrapy.Field(input_processor=MapCompose(remove_tags, correct_spec))
    link = scrapy.Field(output_processor=TakeFirst())
    search = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field()

