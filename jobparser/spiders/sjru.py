import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['www.superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response: HtmlResponse):
        links = response.xpath("//div[@class='_3mfro PlM3e _2JVkc _3LJqf']/a[contains(@class, 'icMQ_')]/@href").extract()
        next_page = response.xpath("//a[contains(@class,'f-test-button-dalshe')]/@href").extract_first()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//span[@class='_3mfro _2Wp8I PlM3e _2JVkc']/text()").extract()
        link = response.request.url
        yield JobparserItem(name=name, salary=salary, link=link)
