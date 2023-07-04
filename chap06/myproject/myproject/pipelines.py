# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from pymongo import MongoClient


class ValidationPipeline:
    """
    Itemを検証するPipeline
    """
    def process_item(self, item, spider):
        if not item['title']:
            # titleフィールドが取得できていない場合は破棄する。
            # DropItem()の引数は破棄する理由を表すメッセージ。
            raise DropItem('Missing title')

        return item # titleフィールドが正しく取得できている場合。


class MongoPipeline:
    """
    ItemをMongoDBに保存するPipeline。
    """

    def open_spider(self, spider):
        """
        Spiderの開始時にMongoDBに接続する。


        Args:
            spider (_type_): _description_
        """
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['scraping-book']
        self.collection = self.db['items']


    def close_spider(self, spider):
        """
        Spiderの終了時にMongoDBへの接続を切断する。

        Args:
            spider (_type_): _description_
        """
        self.client.close()


    def process_item(self, item, spider):
        """
        Itemをコレクションに追加する。

        Args:
            spider (_type_): _description_
        """
        # insert_one()の引数は書き換えられるので、コピーしたdictを渡す。
        self.collection.insert_one(dict(item))
        return item
