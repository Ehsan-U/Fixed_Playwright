import scrapy
from scrapy.loader import ItemLoader

from car_tracker.items import Listing
from car_tracker.common import parseTitle, parseMileage

import os




class RennSpider(scrapy.Spider):
	name = 'renn_spider'
	allowed_domains = ['rennlist.com']
	start_urls = ['https://rennlist.com/forums/market/vehicles']

	custom_settings = {
			'FEED_URI': 'renn_listings.csv',
			'FEED_FORMAT': 'csv',
		 }

	def parse(self, response):
		current_page = 1
		
		listings = response.xpath('//*[@id="search-result-vehicle"]//div[@class="item-summary"]//a')

		for listing in listings:
			title = listing.xpath('text()').get()
			url = listing.xpath('@href').get()
			if 'WTB' in title.upper():
				continue
			else:
				yield response.follow(url, callback = self.parse_listing)


		next_page = response.xpath('//a[@rel="next"]//@href').get()
		if next_page:
			next_page_url = os.path.join('https://rennlist.com', 'forums', next_page)
			yield response.follow(next_page_url, callback = self.parse)



	def parse_listing(self, response):
		listing = ItemLoader(item = Listing(), response = response)

		title = response.xpath('//h2[@class="threadsubtitle"]//text()').get()
		title_data = parseTitle(title)

		subtitle = response.xpath('//h1[@class="threadtitle"]//text()').get().strip()

		listing.add_value('year', title_data['year'])

		listing.add_value('make', title_data['make'])

		listing.add_value('model', title_data['model'])

		vin = response.xpath('//li[span="VIN"]//span[2]//text()').get()
		listing.add_value('vin', vin)

		miles = response.xpath('//li[span="Mileage"]//span[2]//text()').get()
		listing.add_value('miles', miles)

		transmission = response.xpath('//li[span="Transmission"]//span[2]//text()').get()
		listing.add_value('transmission', transmission)

		color = response.xpath('//li[span="Exterior Color"]//span[2]//text()').get()
		listing.add_value('color', color)

		location = response.xpath('//li[span="Location"]//span[2]//text()').get()
		listing.add_value('location', location)

		price = response.xpath('//span[@class="price"]//text()').get().strip()
		listing.add_value('price', price)

		return listing.load_item()





