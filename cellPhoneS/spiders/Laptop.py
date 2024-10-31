import scrapy
from ..login import *
import time
from cellPhoneS.items import LaptopItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.selector import Selector
import logging
from ..config import *
# Set the logging level for Selenium to WARNING
logging.getLogger('selenium').setLevel(logging.CRITICAL)

class LaptopSpider(scrapy.Spider):
    name = "Laptop"
    allowed_domains = ["cellphones.com.vn"]
    start_urls = ["https://cellphones.com.vn/"]
    #Account info
    phone = PHONE
    pw = PW
    cookies = login(phone, pw)

    custom_settings = {
        "USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    
    def __init__(self):
         # Set up Chrome options for headless mode
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")  # Run in headless mode
        
        # Initialize the WebDriver with the specified options
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def start_request(self):
        request = scrapy.Request("https://cellphones.com.vn/", callback = self.parse, cookies = self.cookies)
        yield request

    def parse(self, response):
        laptop_link = response.xpath("//div[@class = 'label-menu-tree']/a/@href").get()
        if laptop_link:
            yield response.follow(laptop_link, callback=self.parse_laptop_brands)
            

    def parse_laptop_brands(self, response):
        brand_links = response.xpath("//div[@class = 'list-brand']/a/@href").getall()
        # Follow each brand link
        unique = []
        for link in brand_links:
            if(link not in unique):
                unique.append(link)

        for link in unique:
            yield response.follow(link, callback=self.parse_brand_page)
            
            

    
    def parse_brand_page(self, response):
         # Locate the "Show more" button and click it
        self.driver.get(response.url)
        if (response.url == "https://cellphones.com.vn/laptop/dell.html"):
            for i in range(3):
                show_more_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@class='button btn-show-more button__show-more-product']"))
                ) 
                
                if show_more_button.is_displayed() and show_more_button.is_enabled():
                    show_more_button.click()  # Click the "Show more" button
    
                    
        # else:
        while True:
            try:
                show_more_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@class='button btn-show-more button__show-more-product']"))
                ) 
                
                if show_more_button.is_displayed() and show_more_button.is_enabled():
                    show_more_button.click()  # Click the "Show more" button

                else: 
                    break
            except Exception as e:
                break
            

            
        # Get the updated page source after clicking "Show more"
        updated_page_source = self.driver.page_source
        selector = Selector(text=updated_page_source)  # Create a Scrapy Selector from the updated page source

        # Extract laptop links
        laptop_links = selector.xpath("//div[@class='product-info-container product-item']/div[@class = 'product-info']/a/@href").getall()
        for link in laptop_links:
            yield response.follow(link, callback = self.parse_laptop)
            
            

           
    
    def parse_laptop(self, response):   
        
        self.driver.get(response.url)
        # Wait for the title and price elements to be present
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='box-product-name']/h1"))
            )
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//span[@class='item-variant-price']"))
            )

        except Exception as e:
            return  # Exit if elements are not found

        
        scroll_pause_time = 1 
        scroll_increment = 500  
        current_scroll_position = 0

        while True:
            current_scroll_position += scroll_increment
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll_position});")
            time.sleep(scroll_pause_time)
            new_spec_elements = self.driver.find_elements(By.XPATH, "//ul[@class='technical-content']/li")
            if len(new_spec_elements) == 0:
                continue
            else:
                break
        updated_page_source = self.driver.page_source
        selector = Selector(text=updated_page_source)

        # Check if title and price elements are present
        title_element = selector.xpath("//div[@class='box-product-name']/h1/text()")
        price_element = selector.xpath("//span[@class='item-variant-price']/text()")
        # Click the button to show all specifications
        try:
            spec_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[@class='button button__show-modal-technical my-3 is-flex is-justify-content-center']"))
                ) 
                
            self.driver.execute_script("arguments[0].click();", spec_button)  # Click the button using JavaScript
            time.sleep(1)  # Wait for the specifications to load
        except Exception as e:
            pass

    # Update the page source to include all specifications
        updated_page_source = self.driver.page_source
        selector = Selector(text=updated_page_source)

        spec_element = selector.xpath("//div[@class = 'modal is-active']//section[@class = 'modal-card-body']//div[@class = 'modal-item-description mx-2']//div[@class = 'px-3 py-2 is-flex is-align-items-center is-justify-content-space-between']")


        if title_element and price_element:
            title = title_element.get()
            price = price_element.get()
            specs = dict()
            for spec in spec_element:
                if( spec.xpath("./p/a")):
                    key = spec.xpath("./p/a/text()").get()
                else:
                    key = spec.xpath("./p/text()").get()
                value = spec.xpath("./div/text()").getall()
                if(len(value) == 1):
                    if (", " in value[0]):
                        tmp = value[0].split(", ")
                        value = tmp
                    else:
                        value = value[0]
                specs[key] = value

            laptop = LaptopItem()
            laptop['title'] = title
            laptop['price'] = price
            laptop['specs'] = specs
            laptop['url'] = response.url
            
            yield laptop
        