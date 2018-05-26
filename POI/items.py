# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PoiItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    district = scrapy.Field()
    address = scrapy.Field()
    phone_num = scrapy.Field()
    category = scrapy.Field()
    tag = scrapy.Field()
    Geodetic_coordinate = scrapy.Field()
    Mars_coordinate = scrapy.Field()
    baidu_coordinate = scrapy.Field()
