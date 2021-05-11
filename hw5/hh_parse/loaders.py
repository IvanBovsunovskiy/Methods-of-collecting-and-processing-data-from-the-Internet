from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from urllib.parse import urljoin


def clear_itm(itm):
    return itm.replace("\xa0", " ")


def space_delete_descr(descr):
    if descr == ' ':
        return ''
    else:
        descr += ' '
        return descr


def get_url(itm):
    return urljoin("https://hh.ru/", itm)


class PositionLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = MapCompose(clear_itm, space_delete_descr)
    title_out = Join('')
    salary_in = MapCompose(clear_itm)
    salary_out = Join('')
    description_in = MapCompose(clear_itm, space_delete_descr)
    description_out = Join('')
    skills_in = MapCompose(clear_itm)
    company_url_in = MapCompose(get_url)
    company_url_out = TakeFirst()


class AuthorLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = MapCompose(clear_itm, space_delete_descr)
    title_out = Join('')
    site_out = TakeFirst()
    description_in = MapCompose(clear_itm, space_delete_descr)
    description_out = Join('')
