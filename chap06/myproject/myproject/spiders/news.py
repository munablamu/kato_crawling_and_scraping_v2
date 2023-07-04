import scrapy

from myproject.items import Headline


class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["news.yahoo.co.jp"]
    start_urls = ["https://news.yahoo.co.jp"]


    def parse(self, response):
        """
        トップページのトピックス一覧から個々のトピックスへのリンクを抜き出して表示する。

        Args:
            response (_type_): _description_
        """
        for url in response.css('#uamods-topics a::attr("href")').re(r'/pickup/\d+$'):
            yield response.follow(url, self.parse_topics)


    def parse_topics(self, response):
        """
        トピックスのページからタイトルと本文を抜き出す。

        Args:
            response (_type_): _description_
        """
        item = Headline()
        item['title'] = response.css('article span p::text').get()
        item['body']  = response.css('article div[data-ual-view-type="digest"] > p').xpath('string()').get().replace('\u3000', '')
        yield item
