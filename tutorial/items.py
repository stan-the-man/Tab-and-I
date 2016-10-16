# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DmozItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    desc = scrapy.Field()


class TabItem(scrapy.Item):
    tab = scrapy.Field()
    tuning = scrapy.Field()
    artist = scrapy.Field()
    song = scrapy.Field()
    capo = scrapy.Field()
    tab_author = scrapy.Field()
