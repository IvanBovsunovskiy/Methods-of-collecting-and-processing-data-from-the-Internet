from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst


class InstagramTagLoader(ItemLoader):
    default_item_class = {}
    date_parse_out = TakeFirst()
    data_out = TakeFirst()


class InstagramPostLoader(ItemLoader):
    default_item_class = {}
    date_parse_out = TakeFirst()
    data_out = TakeFirst()
