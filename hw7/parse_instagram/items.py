# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

"""
Все структуры должны иметь след вид
date_parse (datetime) время когда произошло создание структуры
data - данные полученые от инстаграм
Скачать изображения всех постов и сохранить на диск
"""

import scrapy


class ParseInstagramItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    pass


class ParsePostItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()