# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient



class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost',27017)
        self.mongo_base = client.vacansy2710


    def process_item(self, item, spider):

        if spider.name == 'hhru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_hh(item['salary'])
        elif spider.name == 'sjru':
            item['salary_min'], item['salary_max'], item['currency'] = self.process_salary_sj(item['salary'])
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)


        #print(salary_min, salary_max, currency)
        return item

    def _str_to_int(self, salary):
        """
        Remove hard space and convert to int

        """
        salary = salary.replace(u'\xa0', '')
        return int(salary)

    def process_salary_hh(self, salary):
        if salary[0] == 'з/п не указана':
            return None, None, None
        else:
            currency = salary[-2]

            if salary[0] == 'от ':
                salary_min = self._str_to_int(salary[1])
                if salary[2] == ' до ':
                     salary_max = self._str_to_int(salary[3])
                else:
                     salary_max = None
            elif salary[0] == 'до ':
                salary_max = self._str_to_int(salary[1])
                salary_min = None
            else:
                return None, None, None

        return salary_min, salary_max, currency

    def process_salary_sj(self, salary):
        if salary[0] == 'По договорённости':
            return None, None, None
        else:
            salary = ' '.join(salary).replace(u'\xa0', ' ').split()
            currency = salary[-1]
            if salary[0] == 'от':
                salary_min = self._str_to_int(salary[1]+salary[2])
                salary_max =None
            elif salary[0] == 'до':
                salary_max = self._str_to_int(salary[1] + salary[2])
                salary_min = None
            elif salary[0].isdigit() and len(salary)==4:
                salary_min = self._str_to_int(salary[0] + salary[1])
                salary_max = self._str_to_int(salary[2] + salary[3])
            elif salary[0].isdigit() and len(salary)==3:
                salary_min = self._str_to_int(salary[0] + salary[1])
                salary_max = self._str_to_int(salary[0] + salary[1])
            else:
                return None, None, None

        return salary_min, salary_max, currency