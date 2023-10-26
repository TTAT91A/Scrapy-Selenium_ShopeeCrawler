from typing import Any, Iterable, Optional
import scrapy
from scrapy.http import Request, Response
import datetime
from scrapy.utils.response import open_in_browser
from datetime import date

class ShopeeSpider(scrapy.Spider):
    name = "shopee"
    def __init__(self):
        self.starting_time = datetime.datetime.now()
        self.start_urls = ['https://shopee.vn/coolmate.vn', 'https://shopee.vn/rough.vn']
        # self.start_urls = ['https://shopee.vn/rough.vn']
    
    def start_requests(self):
        for url in self.start_urls:
            self.stop_loop = False
            index = 0
            while not self.stop_loop:
                link = url + '?page='+str(index)+'&sortBy=pop'
                yield scrapy.Request(url=link, callback=self.parse_link_page)
                index += 1
    
    def parse_link_page(self, response):#get link of each product
        products = response.css("div.shop-search-result-view__item.col-xs-2-4")
        if len(products) != 0:
            for product in products:
                product_link = "https://shopee.vn/" + product.css("a::attr(href)").get()
                yield scrapy.Request(url=product_link,callback=self.parse_product)
        else:
            self.stop_loop = True
            
    def parse_product(self, response):
        shop = response.css("div.VlDReK::text").get()
        product_name = response.css("div._44qnta span::text").get()
        rating_point = float(response.css("div._1k47d8._046PXf::text").get())
        number_of_reviews = response.css("div._1k47d8::text")[-1].get()
        quantity_sold = response.css("div.e9sAa2::text").get()
        current_price = response.css("div.pqTWkA::text").get()
        original_price = response.css("div.Y3DvsN::text").get() #maybe null
        discount = response.css("div._0voski::text").get() #maybe null
        date_updated = str(date.today())
        items = {
            'Shop': shop,
            'Product Name':product_name,
            'Rating Point': rating_point,
            'Number Of Review': number_of_reviews,
            'Quantity Sold': quantity_sold,
            'Current Price': current_price,
            'Original Price': original_price,
            'Discount': discount,
            'Updated': date_updated,
            'Detail': {}
        }

        product_details = response.css("div.dR8kXc")

        #get category of product
        category_name = product_details[0].css("label::text").get()
        category_value = product_details[0].css("a::text")[-1].get()
        #get brand of product
        brand_name = product_details[1].css("label::text").get()
        brand_value = product_details[1].css("a::text").get()

        items['Detail'][category_name] = category_value
        items['Detail'][brand_name] = brand_value

        for product_detail in product_details[2:]:
            name = product_detail.css("label::text").get()
            value = product_detail.css("div::text").get()
            items['Detail'][name] = value
        yield items
        # pass
    
    def close(self):
        self.ending_time = datetime.datetime.now()
        duration = self.ending_time - self.starting_time
        print("Total time: ",duration)
