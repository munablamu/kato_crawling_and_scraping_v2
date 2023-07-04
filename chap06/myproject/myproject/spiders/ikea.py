from scrapy.spiders import SitemapSpider


class IkeaSpider(SitemapSpider):
    name = 'ikea'
    allowed_domains = ['www.ikea.com']

    # この設定がないと 504 Gateway Time-out となることがある。
    # settings.pyでUser_Agentを設定している場合、この設定は削除して良い。
    custom_settings = {
        'USER_AGENT': 'ikeabot',
    }

    # XMLサイトマップのURLのリスト
    # robots.txtのURLを指定すると、SitemapデレクティブからXMLサイトマップのURLを取得する。
    sitemap_urls = [
        'https://www.ikea.com/robots.txt',
    ]

    # サイトマップインデックスからたどるサイトマップURLの正規表現のリスト
    # このリストの正規表現にマッチするURLのサイトマップのみをたどる。
    # sitemap_followを指定しない場合は、すべてのサイトマップをたどる。
    sitemap_follow = [
        r'prod-ja-JP', # 日本語の製品のサイトマップのみをたどる。
    ]

    # サイトマップに含まれるURLを処理するコールバック関数を指定するルールのリスト
    # ルールは（正規表現、正規表現にマッチするURLを処理するコールバック関数）という２要素のタプルで指定する。
    # sitemap_rulesを指定しない場合はすべてのURLのコールバック関数はparseメソッドとなる。
    sitemap_rules = [
        (r'/products/', 'parse_product'), # 製品ページをparse_productで処理する。
    ]

    def parse_product(self, response):
        # 製品ページから製品の情報を抜き出す。
        yield {
            'url' : response.url, # URL
            'name': response.css('#name::text').get().strip(), # 名前
            'type': response.css('#type::text').get().strip(), # 種類
            # 価格。円記号と数値の間に \xa0(HTMLでは&nbsp;)が含まれているのでこれをスペースに置きかえる。
            'price': response.css('#price1::text').re_first('[\S\xa0]+').replace('\xa0', ' '),
        }
