import json
import re
import random
from urllib.parse import urljoin
import scrapy
from scrapy_playwright.page import PageMethod
from scrapy.selector import Selector
from rich.console import Console
from scrapy.loader import ItemLoader
from car_tracker.items import Listing

class CabSpider(scrapy.Spider):
	data = {}
	not_required = ['seller','body style','seller type','drivetrain']
	name = 'cab_spider'
	custom_settings = {
		'FEED_URI': 'cab_listings.csv',
		'FEED_FORMAT': 'csv',
	 }
	urls = set()
	counter = 0
	page_count = 1
	allowed_domains = ['carsandbids.com']
	con = Console()

	def start_requests(self):
		url = "https://carsandbids.com"
		yield scrapy.Request(
			url,callback=self.parse,
			meta={"playwright":True,"playwright_include_page":True,"playwright_page_methods":[
				PageMethod("wait_for_selector","//li[@class='auction-item ']"),
			]},
			errback=self.errback,
			)

	# parse main page & extract url of each car page & also handle pagination
	async def parse(self,response):
		page = response.meta.get("playwright_page")
		source = await page.content()
		sel = Selector(text=source)
		for link in sel.xpath("//div[@class='auction-title']/a/@href").getall():
			link = response.urljoin(link)
			self.urls.add(link)
		self.con.print(len(self.urls))
		await page.close()
		self.page_count+=1
		if self.page_count <=3:
				url = f"https://carsandbids.com/?page={self.page_count}"
				yield scrapy.Request(
					url,callback=self.parse,
					meta={"playwright":True,"playwright_include_page":True,"playwright_page_methods":[
						PageMethod("wait_for_selector","//li[@class='auction-item ']"),
					]},
					errback=self.errback,
					)
		else:
			for url in self.urls:
				yield scrapy.Request(
				url,callback=self.parse_car,
				meta={"playwright":True,"playwright_include_page":True,"playwright_page_methods":[
					PageMethod("wait_for_selector","//div[@class='quick-facts']"),
				]},
				errback=self.errback,
				)

	# parsing car page
	async def parse_car(self,response):
		try:
			loader = ItemLoader(item=Listing(),response=response)
			sel = Selector(text=response.body)
			year = sel.xpath("//div[@class='auction-title']/h1/text()").get()[:4]
			raw_title = sel.xpath("//div[@class='auction-title']/h1/text()").get()
			raw_subtitle = sel.xpath("//div[@class='d-md-flex justify-content-between flex-wrap']/h2/text()").get()
			if sel.xpath("//div[@class='d-md-flex justify-content-between flex-wrap']//h2/span").get():
				no_reserver = "True"
			else:
				no_reserver = "False"
			source = response.url
			price = sel.xpath("//span[@class='value']/span[@class='bid-value']/text()").get()
			main_image = sel.xpath("//div[@class='preload-wrap main loaded']/img/@src").get()
			images = ",".join(sel.xpath("//div[@class='preload-wrap  loaded']/img/@src").getall())
			if "kilometers" in sel.xpath("//div[@class='detail-wrapper']").get().lower():
				kilometers = "True"
			else:
				kilometers = "False"
			dt_tags = sel.xpath("//div[@class='quick-facts']//dt")
			dd_tags = sel.xpath("//div[@class='quick-facts']//dd")
			for dt,dd in zip(dt_tags,dd_tags):
				if dd.xpath(".//a"):
					if not dt.xpath(".//text()").get().lower() in self.not_required:
						loader.add_value(dt.xpath(".//text()").get(),dd.xpath(".//a/text()").get())
				else:
					if not dt.xpath(".//text()").get().lower() in self.not_required:
						if dt.xpath(".//text()").get() == "Mileage":
							raw_miles = dd.xpath(".//text()").get()
							if "TMU" in raw_miles:
								tmu = "True"
							else:
								tmu = "False"
							Mileage = ''
							miles_characters = list(dd.xpath(".//text()").get())
							for c in miles_characters:
								if c.isdigit():
									Mileage +=c
							# data["Mileage"] = Mileage
							loader.add_value('miles',Mileage)
						elif "title" in dt.xpath(".//text()").get().lower():
							loader.add_value("title_status",dd.xpath(".//text()").get())
						elif "exterior" in dt.xpath(".//text()").get().lower():
							loader.add_value("color",dd.xpath(".//text()").get())
						elif "interior" in dt.xpath(".//text()").get().lower():
							loader.add_value("interior_color",dd.xpath(".//text()").get())
						else:
							loader.add_value(dt.xpath(".//text()").get(), dd.xpath(".//text()").get())
	
			loader.add_value("year",year)
			loader.add_value("price",price)
			loader.add_value("kilometers",kilometers)
			loader.add_value("tmu",tmu)
			loader.add_value("no_reserve",no_reserver)
			loader.add_value("url",response.url)
			loader.add_value("raw_title",raw_title)
			loader.add_value("raw_subtitle",raw_subtitle)
			loader.add_value("raw_miles",raw_miles)
			loader.add_value("source",response.url)
			loader.add_value("main_image",main_image)
			loader.add_value("all_images",images)
			page = response.meta.get("playwright_page")
			await page.close()
			self.counter+=1
			self.con.print(f"[+] [bold green]]Processed Items: [bold cyan]{self.counter},[bold green] Remaining Items: [bold cyan]{len(self.urls)-self.counter}")
			yield loader.load_item()
		# self.con.print(data) 
		except:
			self.con.print_exception()
	async def errback(self,failure):
		page = failure.request.meta["playwright_page"]
		await page.close()