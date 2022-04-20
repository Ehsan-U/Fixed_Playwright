import scrapy
from scrapy.loader import ItemLoader

from car_tracker.items import Listing
from car_tracker.common import parseTitle, parseMileage, parsePrice


class BatSpider(scrapy.Spider):
	name = 'bat_spider'
	allowed_domains = ['bringatrailer.com']
	start_urls = ['https://bringatrailer.com/auctions/']

	custom_settings = {
			'FEED_URI': 'bat_listings.csv',
			'FEED_FORMAT': 'csv',
		 }

	def parse(self, response):
		listings = response.xpath('(//div[@class="auctions-item"])')

		for listing in listings:
			url = listing.xpath('div//*[@class="auctions-item-title"]//@href').get()
			title = listing.xpath('div//*[@class="auctions-item-title"]//text()').get()
			yield response.follow(url, callback = self.parse_listing)


	def parse_listing(self, response):
		listing = ItemLoader(item = Listing(), response = response)

		listing_title = response.css('.post-title::text').get()
		title_data = parseTitle(listing_title)

		listing.add_value('make', title_data.get('make', ''))
		listing.add_value('model', title_data.get('model', ''))
		listing.add_value('year', title_data.get('year', ''))
		listing.add_value('raw_title', listing_title)

		vin = response.xpath('(//*[@class="essentials"]//li)[contains(text(), "Chassis")]//a//text()').get()
		listing.add_value('vin', vin)

		miles = response.xpath('(//*[@class="essentials"]//li)[contains(text(), "Miles")]//text()').get()
		parsed_miles, kilometers, tmu = parseMileage(miles)
		listing.add_value('miles', parsed_miles)
		listing.add_value('raw_miles', miles)
		listing.add_value('tmu', tmu)
		listing.add_value('kilometers', kilometers)

		listing.add_value('url', response.request.url)

		listing.add_value('source', 'Bring a Trailer')

		main_image = response.xpath('//div[@class="column column-post-image"]/img/@src').get()
		main_image_split = main_image.split('?')
		main_image_split.pop(-1)
		main_image = ''.join(main_image_split)
		listing.add_value('main_image', main_image)

		price = response.xpath('//strong[@class="info-value"]/text()').get()
		parsed_price = parsePrice(price)
		listing.add_value('price', parsed_price)
		


		return listing.load_item()



