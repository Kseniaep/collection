#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import logging
from pymongo import MongoClient

chromedriver = '/home/ksenia/PycharmProjects/collection/chromedriver'

logging.basicConfig(format='%(asctime)s %(levelname)-5s %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

client = MongoClient('localhost', 27017)
db = client.messages

chrome_options = Options()
chrome_options.add_argument( "--headless" ) #Режим без интерфейса
browser = webdriver.Chrome(chromedriver, options=chrome_options)

def load_new_data(records):
    """
    Load news to Mongodb
    """
    counter = 0
    for record in records:
        filter = {'title': record['title'],
                  'body': record['body'],
                  'from_mail': record['from_mail'],
                  'date': record['date']
                 }
        if db.messages.count_documents(filter=filter) == 0:
            db.messages.insert_one(record)
            counter += 1
    logger.info(f'Loaded {counter} messages.')

# browser  = webdriver.Chrome(chromedriver)
browser.get('http://www.mail.ru')
# send login
username = browser.find_element_by_id("mailbox:login-input")
username.send_keys("study.ai_172@mail.ru")

browser.find_element_by_id("mailbox:submit-button").click()
# send password
password = browser.find_element_by_id("mailbox:password-input")
password.send_keys("NextPassword172")

browser.find_element_by_id("mailbox:submit-button").click()

try:
    element = WebDriverWait(browser, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'js-letter-list-item'))
    )
finally:
    pass
# open first message
browser.find_element_by_class_name('js-letter-list-item').click()

next_page = True
# create action chain object
action = ActionChains(browser).key_down(Keys.CONTROL)\
    .send_keys(Keys.ARROW_DOWN).key_up(Keys.CONTROL)
delay = 3 # seconds
step = 100/1000 # time between requests
messages_list = []
while next_page:
    try:
        element = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "letter__body"))
        )
    finally:
        pass
    message = {}
    try:
        message['title'] = browser\
        .find_element_by_class_name('thread__subject-line')\
            .text
        logger.debug(message['title'])
        message['body'] = browser.find_element_by_class_name('letter__body').text
        logger.debug(message['body'])
        message['from_mail'] = browser\
            .find_element_by_css_selector('span.letter-contact')\
            .get_attribute('title')
        logger.debug(message['from_mail'])
        message['date'] = browser\
            .find_element_by_css_selector('div.letter__date').text
        logger.debug(message['date'])
        logger.debug(message['title'])
        current_url = browser.current_url
        messages_list.append(message)
    except Exception as e:
        logger.warning("Message missed")
        logger.warning(e)
    # perform the oepration
    action.perform()

    waited_time = 0
    while (current_url == browser.current_url) and (waited_time < delay):
        time.sleep(step)
        waited_time += step
        logger.debug(f'Waited_time {waited_time} s')
   

    if browser.find_elements_by_css_selector('span.button2_disabled'):
        logger.info('End of messages')
        next_page = False
    else:
        logger.info('Next message')
browser.close()

load_new_data(messages_list)

# db.news.delete_many({})

