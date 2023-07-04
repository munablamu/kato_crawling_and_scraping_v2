from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from myproject.items import Restaurant


class TabelogSpider(CrawlSpider):
    name = 'tabelog'
    allowed_domains = ['tabelog.com']
    start_urls = [
        'https://tabelog.com/tokyo/rstLst/lunch/?LstCosT=2&RdoCosTp=1',
    ]

    rules = [
        Rule(LinkExtractor(allow=r'/\w+/rstLst/lunch/\d/')),
        Rule(LinkExtractor(allow=r'\w+/A\d+/A\d+/\d+/$'), callback='parse_restaurant'),
    ]


    def parse_restaurant(self, response):
        """
        レストランの詳細ページをパースする。

        Args:
            response (_type_): _description_
        """
        # Google Static Mapsの画像のURLから緯度と経度を取得。
        latitude, longitude = response.css(
            'img.js-map-lazyload::attr("data-original")').re(r'markers=.*?%7C([\d.]+),([\d.]+)')

        # キーの値を指定してRestaurantオブジェクトを作成。
        item = Restaurant(
            name=response.css('.display-name').xpath('string()').get().strip(),
            address=response.css('.rstinfo-table__address').xpath('string()').get().strip(),
            latitude=latitude,
            longitude=longitude,
            station=response.css('dt:contains("最寄り駅")+dd span::text').get(),
            score=response.css('[rel="v:rating"] span::text').get(),
        )

        yield item
