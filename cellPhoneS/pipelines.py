# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CellphonesPipeline:
    def process_item(self, item, spider):

        price = item['price']
        temp = price.replace(" ","").replace("\n", "").replace(".", "")
        item['price'] = float(temp[:-1])
        return item

import csv

class CsvExportPipeline:
    def open_spider(self, spider):
        self.file = open('cellphoneS_laptops.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Title', 'Price', 'Specs', 'URL'])  # Write header

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        specs_str = ', '.join([f"{k}: {v}" for k, v in item['specs'].items()])  # Convert specs to string
        self.writer.writerow([item['title'], item['price'], specs_str, item['url']])
        return item
