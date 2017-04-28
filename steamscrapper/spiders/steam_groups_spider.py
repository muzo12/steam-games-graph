# run this script with command:
# scrapy runspider steam_groups_spider.py -o users.json
# then feed found users into users_to_profiles_or_ids.py

import json
import scrapy

from steamscrapper.items import SteamUsersItem  # todo: delete?

class SteamUsersSpider(scrapy.spiders.CrawlSpider):
    name = "steamusers"
    allowed_domains = ["steamcommunity.com"]
    base_url = "http://steamcommunity.com/groups/tradingcards/members?p=%s&content_only=true"   # starting group
    start_urls = [base_url % 1]

    def parse(self, response):
        for user in response.css('a.linkFriend'):
            yield {
                'href' : user.xpath('.//@href').extract_first()
            }

        # IS THERE ANOTHER URL?
        buttons = response.css('div.pageLinks')[0].extract()
        fetchNextPage = not ("pagebtn disabled" in buttons[-40:])
        print(fetchNextPage)

        # WHAT IS NEXT URL?
        if fetchNextPage:
            next_page = response.css('div.pageLinks')[0].xpath(".//a[@class='pagebtn']/@href").extract()[-1]
            next_page = next_page.replace("#members/", "/members")
            next_page += "&content_only=true"
            
            print("!!! NEXT PAGE !!!\n"+
                next_page+
                "\n")

            yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)
