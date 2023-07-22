# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AihitdataItem(scrapy.Item):
    # define the fields for your item here like:
    company_name = scrapy.Field()
    company_address = scrapy.Field()
    company_url = scrapy.Field()
    company_email = scrapy.Field()
    company_fax = scrapy.Field()
    company_phone_number = scrapy.Field()
    company_description = scrapy.Field()
    company_primary_location = scrapy.Field()

    def set_all(self, value):
        for keys,_ in self.fields.items():
            self[keys] = value
