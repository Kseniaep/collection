from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlin import settings
from leroymerlin.spiders.leroiru import LeroySpider


if __name__ =='__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    q = input('Введите желаемый товар')
    # q = "ель"
    process = CrawlerProcess(settings = crawler_settings)
    process.crawl(LeroySpider, search=q)


    process.start()





