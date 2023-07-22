import os
from urllib.parse import urlencode
import scrapy
from scrapy.http import FormRequest
from dotenv import load_dotenv
from ..items import AihitdataItem

load_dotenv()
_PROXY_URL = f"http://scraperapi:{os.getenv('API')}@proxy-server.scraperapi.com:8001?render=true"

class AihitdataSpider(scrapy.Spider):
    name = 'aihitdata'

    def start_requests(self):
        login_url = 'https://www.aihitdata.com/login/'
        yield scrapy.Request(
            login_url,
            callback=self.login,
            meta={'proxy': _PROXY_URL}
            )
    
    def login(self, response):
        token = response.css("form input[name=csrf_token]::attr(value)").extract_first()
        yield FormRequest.from_response(
            response,
            formdata = {
                'csrf_token': token,
                'email': os.getenv("email"),
                'password': os.getenv('password')
            },
            callback=self.parse)

    def parse(self, response, **kwargs):
        yield scrapy.Request(
            'https://www.aihitdata.com/search/companies?c=&i=geothermal+consulting&l=&k=&r=&t=&w=1&e=1&rc=&v=3',
            callback=self.start_scrapping,
            meta={'proxy': _PROXY_URL}
            )
        
    def start_scrapping(self, response):
        top_links = response.css('.panel-body .panel-body a::attr(href)').extract()
        for link in top_links:
            if 'geologica-geothermal-group' in link:
                yield scrapy.Request(
                    response.urljoin(link),
                    callback=self.follow_company,
                    meta={'proxy': _PROXY_URL}
                    )
        
        # iterate through all the pages
        # if response.css('.pagination li:nth-child(8) a::attr(title)').extract_first().strip() == 'Next page':
        #     next_page_url = response.css('.pagination li:nth-child(8) a::attr(href)').extract_first()
        #     yield response.follow(response.urljoin(next_page_url), callback=self.start_scrapping)
    
    def follow_company(self, response):
        company_profile = AihitdataItem()
        company_profile.set_all(None)
        company_profile['company_name'] = response.css('.text-info::text').extract_first().strip()
        company_profile['company_description'] = response.css('.panel-body .row+ div::text').extract_first().strip()
        if 'Primary location' in response.css('.grippy-host , .panel-body div+ div:nth-child(4)::text').extract_first().strip():
            company_profile['company_primary_location'] = ','.join(response.css('.panel-body div:nth-child(4) a::text').extract())
        if 'icon-home' in response.css('.grippy-host , .list-inline~ .list-inline li:nth-child(1) i').xpath('@class').extract_first():
            company_profile['company_url'] = response.css('.grippy-host , .list-inline~ .list-inline li:nth-child(1) a::attr(href)').extract_first().strip()
        contact_page = response.css('.grippy-host , .nav-stacked li:nth-child(3) a::attr(href)').extract_first()
        yield scrapy.Request(
            response.urljoin(contact_page),
            callback=self.get_contact_info,
            meta={'proxy': _PROXY_URL},
            cb_kwargs=dict(item_obj=company_profile))
    
    def get_contact_info(self, response, item_obj):
        icon_map_marker = response.css('.text-muted i').xpath('@class').extract_first()
        if icon_map_marker and 'icon-map-marker' in icon_map_marker:
            item_obj['company_address'] = response.css('.text-muted::text').extract_first().strip()
        for selector in response.css('.list-inline:nth-child(5)').css('li'):
            # icon_email = response.css('.list-inline li:nth-child(1) i').xpath('@class').extract_first()
            css_class_name = selector.css('i').xpath('@class').extract_first()
            if ('icon-email' in css_class_name):
                item_obj['company_email'] = selector.css('li a::text').extract_first().strip()
            # icon = response.css('.list-inline li:nth-child(2) i').xpath('@class').extract_first()
            if ('icon-fax' in css_class_name):
                item_obj['company_fax'] = selector.css('li::text').extract_first().strip()
            # icon_phone = response.css('.list-inline li:nth-child(3) i').xpath('@class').extract_first()
            if ('icon-phone' in css_class_name):
                item_obj['company_phone_number'] = response.css('li::text').extract_first().strip()
        yield item_obj
    
