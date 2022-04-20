import scrapy


class AutoTraderSpider(scrapy.Spider):
    name = "autotrader"

    def start_requests(self):
        urls = [
            'https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=forSaleTab_false_0&newSearchFromOverviewPage=true&inventorySearchWidgetType=AUTO&entitySelectingHelper.selectedEntity=c7735&entitySelectingHelper.selectedEntity2=c22960&zip=07446&distance=50000&searchChanged=true&modelChanged=true&filtersModified=true&sortType=undefined&sortDirection=undefined#listing=231248357',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)