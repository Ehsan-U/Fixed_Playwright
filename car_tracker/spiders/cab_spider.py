import scrapy
from scrapy.loader import ItemLoader

from scrapy_splash import SplashRequest

from car_tracker.items import Listing
from car_tracker.common import parseTitle, parseMileage

from w3lib.http import basic_auth_header
from pkgutil import get_data


class CabSpider(scrapy.Spider):
	name = 'cab_spider'
	allowed_domains = ['carsandbids.com']
	start_urls = ['https://carsandbids.com/']

	custom_settings = {
			'FEED_URI': 'cab_listings.csv',
			'FEED_FORMAT': 'csv',
			'FEED_EXPORT_FIELDS': [
				'year',
				'make',
				'model',
				'miles',
				'vin',
				'no_reserve',
				'tmu',
				'kilometers',
				'raw_title',
				'raw_miles',
				'url',
			 ],
		 }

	def __init__(self, *args, **kwargs):
		# to be able to load the Lua script on Scrapy Cloud, make sure your
		# project's setup.py file contains the "package_data" setting, similar
		# to this project's setup.py
		self.LUA_SOURCE = get_data('car_tracker', 'scripts/cab.lua').decode('utf-8')
		super(CabSpider, self).__init__(*args, **kwargs)


	def parse(self, response):
		# listings = response.xpath('(//div[@class="auctions-item"])')

		# for listing in listings:
		# 	url = listing.xpath('div//*[@class="auctions-item-title"]//@href').get()
		# 	title = listing.xpath('div//*[@class="auctions-item-title"]//text()').get()
		# 	yield response.follow(url, callback = self.parse_listing)

		# yield SplashRequest(
		# 	url='https://carsandbids.com',
		# 	endpoint='render.html',
		# 	splash_headers={
		# 		'Authorization': basic_auth_header(self.settings['SPLASH_APIKEY'], ''),
		# 	},
		# 	#args={
		# 		#'lua_source': self.LUA_SOURCE,
		# 	#},
		# 	# tell Splash to cache the lua script, to avoid sending it for every request
		# 	#cache_args=['lua_source'],
		# 	callback = self.parse_listing,
		# )

		yield SplashRequest(
			url=self.start_urls[0], 
			callback=self.parse_listing, 
			endpoint="execute", 
			args={'lua_source': self.LUA_SOURCE},
			splash_headers={
				'Authorization': basic_auth_header(self.settings['SPLASH_APIKEY'], ''),
			},
)

	def parse_listing(self, response):
		listing = ItemLoader(item = Listing(), response = response)

		print ("\n\n\n")
		print (response.text)
		print ("\n\n\n")
