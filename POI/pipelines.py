# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import CsvItemExporter


class POIPipeline(object):
    def __init__(self):
        self.file = open('poi.csv', 'w')
        self.writer = CsvItemExporter(self.file)
        self.writer.start_exporting()

    def process_item(self, item, spider):
        self.writer.export_item(item)
        return item

    def __del__(self):
        self.file.close()
        self.writer.finish_exporting()
