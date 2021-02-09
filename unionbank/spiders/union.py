import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from unionbank.items import Article


class UnionSpider(scrapy.Spider):
    name = 'union'
    start_urls = ['http://www.unionbankuk.com/news']

    def parse(self, response):
        links = response.xpath('//a[@class="readMoreNews"]/@href').getall()
        yield from response.follow_all(links, self.parse_single)

    def parse_single(self, response):
        link = response.xpath('//div[@id="content"]//a[@title]/@href').get()
        date = response.xpath('//span[@class="date"]/text()').get().split()[-1]
        yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get().strip()
        date = datetime.strptime(date, '%d/%m/%Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@id="content"]/p/text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
