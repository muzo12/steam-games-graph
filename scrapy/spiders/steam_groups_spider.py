import json
import scrapy

#from scrapy.spiders import CrawlSpider
#from scrapy import Selector

from steamscrapper.items import SteamUsersItem

class SteamUsersSpider(scrapy.spiders.CrawlSpider):
    name = "steamusers"
    allowed_domains = ["steamcommunity.com"]
    base_url = "http://steamcommunity.com/groups/tradingcards/members?p=%s&content_only=true"
    start_urls = [base_url % 1]

    def parse(self, response):
        #data = json.loads(response.body)
        for user in response.css('a.linkFriend'):
            yield {
                'href' : user.xpath('.//@href').extract_first()
            }
        
        #print(base_url)

        #IS THERE ANOTHER URL?
        buttons = response.css('div.pageLinks')[0].extract()
        fetchNextPage = not ("pagebtn disabled" in buttons[-40:])
        print(fetchNextPage)

        #WHAT IS NEXT URL?
        if fetchNextPage:
            next_page = response.css('div.pageLinks')[0].xpath(".//a[@class='pagebtn']/@href").extract()[-1]
            next_page = next_page.replace("#members/", "/members")
            next_page += "&content_only=true"
            
            print("!!! NEXT PAGE !!!\n"+
                next_page+
                "\n")

            yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)

        #linkresponse.css('div.pageLinks')[0].xpath('.//@href').extract()
        #next_page = response.css('div.pageLinks')[0].xpath(".//a[@class='pagebtn']/@href").extract_first()+"&content_only=true"
        #print("next_page: " + next_page)
        #yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)

