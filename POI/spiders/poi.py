# -*- coding: utf-8 -*-
import re

import scrapy

from POI.items import PoiItem


class PoiSpider(scrapy.Spider):
    name = 'poi'
    allowed_domains = ['poi86.com']
    start_urls = ['http://poi86.com/']

    def parse(self, response):
        print u'[INFO]  正在解析首页信息'
        node_list = response.xpath('//div[@class="layout"]/div[1]//ul[@class="list-group"]/li')[:1]
        for node in node_list:
            province = node.xpath('div/div[1]/a/strong/text()').extract_first()
            province_code = node.xpath('div/div[1]/a/small/text()').extract_first()
            try:
                province = province + '(' + province_code + ')'
            except Exception as e:
                print province
                print province_code
            # print province
            province_link = 'http://www.poi86.com/' + node.xpath('div/div[1]/a/@href').extract_first()
            yield scrapy.Request(
                url=province_link,
                callback=self.parse_province,
                headers={'Referer': 'http://www.poi86.com/'},
                meta={'province': province}
            )

    def parse_province(self, response):
        print u'[INFO]  正在解析%s省份信息' % response.meta['province']
        node_list = response.xpath('//ul[@class="list-group"]/li')[:1]
        for node in node_list:
            link = 'http://www.poi86.com/' + node.xpath('a/@href').extract_first()
            if 'city' in link:
                city_link = link
                city = node.xpath('a/text()').extract_first() + '(' + node.xpath('span/text()').extract_first() + ')'
                yield scrapy.Request(
                    url=city_link,
                    callback=self.parse_city,
                    headers={'Referer': response.url},
                    meta={'city': city}
                )
            elif 'district' in link:
                district_link = link
                district = node.xpath('a/text()').extract_first() + '(' + node.xpath(
                    'span/text()').extract_first() + ')'
                yield scrapy.Request(
                    url=district_link,
                    callback=self.parse_district,
                    headers={'Referer': response.url},
                    meta={'district': district}
                )

    def parse_city(self, response):
        print u'[INFO]  正在解析%s城市信息' % response.meta['city']
        node_list = response.xpath('//ul[@class="list-group"]/li')
        for node in node_list:
            district_link = 'http://www.poi86.com/' + node.xpath('a/@href').extract_first()
            district = node.xpath('a/text()').extract_first() + '(' + node.xpath('span/text()').extract_first() + ')'
            yield scrapy.Request(
                url=district_link,
                callback=self.parse_district,
                headers={'Referer': response.url},
                meta={'district': district}
            )

    def parse_district(self, response):
        print u'[INFO]  正在解析第%s页%s地区信息' % (re.search(r'/(\d+)\.html', response.url).group(1), response.meta['district'])
        node_list = response.xpath('//table/tr')[1:]
        for node in node_list:
            town_link = 'http://www.poi86.com/' + node.xpath('td[1]/a/@href').extract_first()
            yield scrapy.Request(
                url=town_link,
                callback=self.parse_town,
                headers={'Referer': response.url}
            )
        if response.xpath(
                '//ul[@class="pagination"]/li[last()-2]/a/@href'):
            next_link = 'http://www.poi86.com/' + response.xpath(
                '//ul[@class="pagination"]/li[last()-2]/a/@href').extract_first()
            if next_link != response.url:
                yield scrapy.Request(
                    url=next_link,
                    headers={'Referer': response.url},
                    callback=self.parse_district,
                    meta=response.meta
                )
        else:
            print response.xpath(
                '//ul[@class="pagination"]/li[last()-2]/a/@href')

    def parse_town(self, response):
        item = PoiItem()
        # 名称
        name = response.xpath('//div[@class="panel-heading"]/h1/text()').extract_first()
        print u'[INFO]  正在解析%s乡村信息' % name
        if not name:
            name = u'无名称'
        item['name'] = name
        # 所属省份:
        province = response.xpath('//div[@class="panel-body"]//li[1]/a/text()').extract_first()
        if not province:
            province = u'没有所属省份'
        item['province'] = province
        if response.xpath('//div[@class="panel-body"]//li[2]/span/text()').extract_first() == u'所属城市:':
            # 所属城市:
            city = response.xpath('//div[@class="panel-body"]//li[2]/a/text()').extract_first()
            if not city:
                city = u'没有所属城市'
            item['city'] = city
            # 所属区县:
            district = response.xpath('//div[@class="panel-body"]//li[3]/a/text()').extract_first()
            if not district:
                district = u'没有所属区县'
            item['district'] = district
        else:
            city = u'没有所属城市'
            item['city'] = city
            # 所属区县:
            district = response.xpath('//div[@class="panel-body"]//li[2]/a/text()').extract_first()
            if not district:
                district = u'没有所属区县'
            item['district'] = district
        # 详细地址:
        address = response.xpath('//div[@class="panel-body"]//li[4]/text()').extract_first()
        if not address:
            address = u'没有详细地址'
        item['address'] = address
        # 电话号码:
        phone_num = response.xpath('//div[@class="panel-body"]//li[5]/text()').extract()
        if phone_num == [u' ']:
            phone_num = u'没有电话号码'
        else:
            phone_num = phone_num[0]
        item['phone_num'] = phone_num.strip()
        # 所属分类:
        category = response.xpath('//div[@class="panel-body"]//li[6]/a/text()')
        if not category:
            category = u'没有所属分类'
        else:
            category = category.extract_first()
        item['category'] = category
        # 所属标签:
        tag = response.xpath('//div[@class="panel-body"]//li[7]/a/text()')
        if not tag:
            tag = u'没有所属标签'
        else:
            tag = response.xpath('//div[@class="panel-body"]//li[7]/a/text()').extract_first() + response.xpath(
                '//div[@class="panel-body"]//li[7]/a/small/text()').extract_first() + ')'
        item['tag'] = tag
        # 大地坐标:
        Geodetic_coordinate = response.xpath('//div[@class="panel-body"]//li[8]/text()').extract_first()
        if not Geodetic_coordinate:
            Geodetic_coordinate = u'没有大地坐标'
        item['Geodetic_coordinate'] = Geodetic_coordinate
        # 火星坐标:
        Mars_coordinate = response.xpath('//div[@class="panel-body"]//li[9]/text()').extract_first()
        if not Mars_coordinate:
            Mars_coordinate = u'没有火星坐标'
        item['Mars_coordinate'] = Mars_coordinate
        # 百度坐标:
        baidu_coordinate = response.xpath('//div[@class="panel-body"]//li[10]/text()').extract_first()
        if not baidu_coordinate:
            baidu_coordinate = u'没有百度坐标'
        item['baidu_coordinate'] = baidu_coordinate
        yield item
