import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import leroymerlinItem
from scrapy.loader import ItemLoader

class LeroySpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']


    def __init__(self, search):
        self.search = search
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response:HtmlResponse):
        goods = response.xpath("//uc-plp-item-new/a[@slot='picture']")
        for good in goods:
            yield response.follow(good, callback=self.parse_good)

    def parse_good(self, response: HtmlResponse):
        loader = ItemLoader(item=leroymerlinItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photos', "//picture[@slot='pictures']/source[contains(@media, '1024px')]/@srcset")
        loader.add_xpath('spec', "//div[@class='def-list__group']")
        loader.add_value('link', response.url)
        loader.add_value('search', self.search)
        yield loader.load_item()

        # name = response.xpath("//h1/text()").extract_first()
        # photos = response.xpath("//div[@class='swiper-slide']/a/@href").extract()
        # yield leroymerlinItem(name=name, photos=photos)
