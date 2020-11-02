import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://izhevsk.hh.ru/search/vacancy?area=&fromSearchLine=true&st=searchVacancy&text=python']

    def parse(self, response: HtmlResponse):
        links = response.xpath("//a[@class='bloko-link HH-LinkModifier']/@href").extract()
        next_page = response.xpath("//a[contains(@class,'HH-Pager-Controls-Next')]/@href").extract_first()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacancy_parse(self, response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        salary = response.xpath("//p/span[@data-qa='bloko-header-2']/text()").extract()
        link = response.request.url
        yield JobparserItem(name=name, salary=salary, link=link)
