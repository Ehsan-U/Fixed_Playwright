import scrapy
from scrapy.loader import ItemLoader

from car_tracker.items import Listing
from car_tracker.common import parseTitle, parseMileage, parsePrice

import os




class PcarSpider(scrapy.Spider):
	name = 'pcar_spider'
	allowed_domains = ['pcarmarket.com']
	start_urls = ['https://www.pcarmarket.com/auction/list/all/']

	custom_settings = {
			'FEED_URI': 'pcar_listings.csv',
			'FEED_FORMAT': 'csv',
		 }

	def parse(self, response):
		current_page = 1
		
		listings = response.xpath('//table/tr')

		for listing in listings:
			title = listing.xpath('td//h2//text()').get()
			relative_path = listing.xpath('td//h2//@href').get()
			url = os.path.join('https://www.pcarmarket.com', relative_path.lstrip('/'))
			yield response.follow(url, callback = self.parse_listing)


		next_page = response.xpath('//div/li[@class="next"]//@href').get()
		if next_page:
			next_page_url = os.path.join(self.start_urls[0], next_page)
			yield response.follow(next_page_url, callback = self.parse)


		## pagination


	def parse_listing(self, response):
		listing = ItemLoader(item = Listing(), response = response)

		title = response.xpath('//h2[@class="blogPostDisplayTitle"]/text()').get().strip()
		title_data = parseTitle(title)

		year = response.xpath('//li[strong = "Year"]/text()').get().lstrip(':').strip()
		listing.add_value('year', year)

		make = response.xpath('//li[strong = "Make"]/text()').get().lstrip(':').strip()
		listing.add_value('make', make)

		model = response.xpath('//li[strong = "Model"]/text()').get().lstrip(':').strip()
		listing.add_value('model', model)

		vin = response.xpath('//li[strong = "VIN"]/text()').get().lstrip(':').strip()
		listing.add_value('vin', vin)

		miles = response.xpath('//li[strong = "Mileage"]/text()').get().lstrip(':').strip()
		parsed_miles, kilometers, tmu = parseMileage(miles)
		listing.add_value('miles', parsed_miles)
		listing.add_value('raw_miles', miles)
		listing.add_value('kilometers', str(kilometers))
		listing.add_value('tmu', str(tmu))

		transmission = response.xpath('//li[strong = "Transmission"]/text()[2]').get().lstrip(':').strip()
		listing.add_value('transmission', transmission)

		title = response.xpath('//li[strong = "Title Status"]/text()[2]').get().lstrip(':').strip()
		listing.add_value('title_status', title)

		color = response.xpath('//li[strong = "Color"]/text()[2]').get().lstrip(':').strip()
		listing.add_value('color', color)

		location = response.xpath('//li[strong = "Location"]/text()[2]').get().lstrip(':').strip()
		listing.add_value('location', location)

		listing.add_value('url', response.request.url)

		listing.add_value('source', 'Pcar Market')

		main_image = response.xpath('//div[@id="draggableAuctionGallery"]//img//@src').get()
		main_image_split = main_image.split('/')
		main_image_split.remove('.thumbnails')
		main_image_split.pop(-1)
		main_image = '/'.join(main_image_split)
		listing.add_value('main_image', main_image)

		all_images = []
		all_images_raw = response.xpath('//div[@id="draggableAuctionGallery"]//img//@src').getall()
		for image in all_images_raw:
			image_split = image.split('/')
			image_split.remove('.thumbnails')
			image_split.pop(-1)
			image_url = '/'.join(image_split)
			all_images.append(image_url)

		all_images = ','.join(all_images)
		listing.add_value('all_images', all_images)

		price = response.xpath('//span[@class="pushed_bid_amount"]/text()').get()
		parsed_price = parsePrice(price)
		listing.add_value('price', parsed_price)

		return listing.load_item()





