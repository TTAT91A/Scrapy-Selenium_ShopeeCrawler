# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from scrapy.http import HtmlResponse
from selenium.common.exceptions import TimeoutException
import json


class ShopeecrawlerSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ShopeecrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        # with open(Path(__file__).with_name('proxy_list.txt'), "r") as f:
        #     self.proxies = f.read().split("\n")
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36")
        self.options.add_argument("window-size=1920,1080")
        prefs = {"profile.managed_default_content_settings.images": 2}
        self.options.add_experimental_option("prefs", prefs)
        self.browser = None
        
    
    def spider_opened(self, spider):
        self.browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        
        # Load the saved cookies
        with open("shopee_cookies.json", "r") as file:
            cookies = json.loads(file.read())

        # Visit Shopee.vn with the saved cookies
        self.browser.get('https://shopee.vn')

        # Add the saved cookies to the current session
        for cookie in cookies:
            self.browser.add_cookie(cookie)

        self.browser.refresh()

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
###################### ##########################################################
        # browser = webdriver.Chrome(service=chrome_service, options=options)
        # # browser.get(request.url)

        # import json
        # # Load the saved cookies
        # with open("shopee_cookies.json", "r") as file:
        #     cookies = json.loads(file.read())

        # # Visit Shopee.vn with the saved cookies
        # browser.get(request.url)

        # # Add the saved cookies to the current session
        # for cookie in cookies:
        #     browser.add_cookie(cookie)
        
        # # Refresh the page to apply the cookies
        # browser.refresh()
        # if request.url.split("?")[0] in spider.start_urls:
        #     try:
        #         WebDriverWait(browser,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.shop-search-result-view")))
        #         print("HomePage is ready")
        #     except TimeoutException:
        #         print("Loading took too much time!")
        # else:
        #     try:
        #         #product page
        #         WebDriverWait(browser,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.product-detail.page-product__detail")))
        #         print("Product's Page is ready")
        #     except TimeoutException:
        #         print("Loading took too much time!")
            
        # browser.get_screenshot_as_file("screenshot.png")

        # body = browser.page_source
        # abc = browser.current_url
        # browser.close()
        # return HtmlResponse(abc,body = body, encoding = 'utf8', request = request)
###########################################################################################
        if self.browser is not None:
            self.browser.get(request.url)
            if request.url.split("?")[0] in spider.start_urls:
                try:
                    WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.shop-search-result-view")))
                    spider.log("Page is ready")
                except TimeoutException:
                    spider.log("Loading took too much time!")
            else:
                try:
                    #product page
                    WebDriverWait(self.browser,5).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div.product-detail.page-product__detail")))
                    spider.log("Page is ready")
                except TimeoutException:
                    spider.log("Loading took too much time!")
            self.browser.get_screenshot_as_file("screenshot.png")

            body = self.browser.page_source
            url = self.browser.current_url
            return HtmlResponse(url, body=body, encoding='utf8', request=request)


    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.    

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    # def spider_opened(self, spider):
    #     spider.logger.info("Spider opened: %s" % spider.name)
    def spider_closed(self, spider, reason):
        if self.browser:
            self.browser.quit()