# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CarTrackerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass



class Listing(scrapy.Item):
	year = scrapy.Field()
	make = scrapy.Field()
	model = scrapy.Field()
	
	vin = scrapy.Field()
	miles = scrapy.Field()
	color = scrapy.Field()
	transmission = scrapy.Field()
	engine = scrapy.Field()
	location = scrapy.Field()
	title_status = scrapy.Field()
	price = scrapy.Field()

	kilometers = scrapy.Field()
	tmu = scrapy.Field()
	no_reserve = scrapy.Field()

	url = scrapy.Field()
	raw_title = scrapy.Field()
	raw_subtitle = scrapy.Field()
	raw_miles = scrapy.Field()
	source = scrapy.Field()

	main_image = scrapy.Field()
	all_images = scrapy.Field()
