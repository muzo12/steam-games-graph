"""
Use scrapy shell when you want to poke around. It helps with getting right xpath queries tremendously.
e.g.: scrapy shell "store.steampowered.com/app/263980/"
and have fun
"""

import json
import scrapy
import time


class AppdataFromAppids(scrapy.spiders.CrawlSpider):
    name = "appdata"
    allowed_domains = ["steamcommunity.com", "steampowered.com"]
    # change the file path!
    appids = open(
        "C:\\Users\\Admin\\Documents\\GitHub\\GamesGraph\\scripts\\wip_data\\_dataframe_merged_appids.txt").read()
    appids_json = json.loads(appids)
    # appids_json = ['appid563560']
    start_urls = ['http://store.steampowered.com/app/' + id.strip('appid') + '/' for id in appids_json]
    start_urls.sort()

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5
    }


    def parse(self, response):
        url = response.url
        request = scrapy.Request(response.url, cookies = {'mature_content': 1, 'birthtime': -31539599, 'lastagecheckage': '1-January-1969'}, callback=self.parse_content)
        request.meta['base_url'] = url
        yield request


    def parse_content(self, response):
        # ORIGINAL URL
        url = response.meta['base_url'].partition("app/")[2].strip("/")

        if response.request == "http://store.steampowered.com/":
            print("!!!\n", "response is blank for url:", url, "\n!!!")

        else:
            # APP ID!
            appid = response.xpath('//link[contains(@rel, "canonical")]/@href').extract_first()
            appid = appid.partition("app/")[2]

            appid = appid.strip("/")

            print("!!!\n", url, "\n", appid, "\n!!!")

            # TITLE!
            title = response.xpath('.//div[@class="apphub_AppName"]/text()').extract_first()

            # TAGS!
            tags = []
            for tag in response.xpath(".//a[@class='app_tag']/text()").extract():
                tag = tag.replace("\r\n", "")
                tag = tag.replace("\t", "")

                tags.append(tag)

            # PRICE, RELEASE DATE, DEVELOPER & PUBLISHER
            price = response.xpath('.//div[@itemprop="offers"]/meta[@itemprop="price"]/@content').extract()
            price_currency = response.xpath('.//div[@itemprop="offers"]/meta[@itemprop="priceCurrency"]/@content').extract()
            developer = response.css('div.details_block').xpath('a[contains(@href, "developer")]/text()').extract()
            publisher = response.css('div.details_block').xpath('a[contains(@href, "publisher")]/text()').extract()
            release_date = response.css('div.release_date').xpath('./span/text()').extract()

            yield {
                'requested_appid': url,
                'appid': appid,
                'title': title,
                'release_date': release_date,
                'price': price,
                'price_currency': price_currency,
                'developer': developer,
                'publisher': publisher,
                'tags': tags
            }

            print(appid, title)


        #time.sleep(1)
