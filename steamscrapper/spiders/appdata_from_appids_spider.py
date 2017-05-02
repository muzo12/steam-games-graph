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
        "C:\\Users\\Admin\\Documents\\GitHub\\GamesGraph\\scripts\\wip_data\\_appids_from_xml.txt").read()
    appids = appids.split('\n')
    #appids = appids.pop()
    print(appids, len(appids))
    #appids_json = json.loads(appids)
    # appids_json = ['appid563560'] # for testing purposes
    #start_urls = ['http://store.steampowered.com/app/' + id.strip('appid') + '/' for id in appids_json]
    start_urls = ['http://store.steampowered.com/app/' + id + '/' for id in appids]
    start_urls.sort()

    custom_settings = {
        'DOWNLOAD_DELAY': 0.75
    }

    def start_requests(self):
        return [scrapy.FormRequest(url,
                                   meta={'req_url': url},
                                   cookies = {'mature_content': 1, 'birthtime': -31539599, 'lastagecheckage': '1-January-1969'},
                                   callback=self.parse_content) for url in self.start_urls]

    def parse_content(self, response):
        print('parse_content\n')
        print('keys:', list(response.meta.keys()))
        for key in list(response.meta.keys()):
            print (key, response.meta[key])

        if response.request == "http://store.steampowered.com/":
            print("!!!\n", "response is blank for url:", url, "\n!!!")

        else:
            # RESPONSE ID!
            appid = response.url
            #appid = response.xpath('//link[contains(@rel, "canonical")]/@href').extract_first()
            appid = appid.partition("app/")[2]
            appid = appid.partition("/")[0]

            # REQUEST APP ID!
            req_appid = response.meta['req_url']
            req_appid = req_appid.partition("app/")[2]
            req_appid = req_appid.strip("/")

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
                'appid': appid,
                'requested_appid': req_appid,
                'title': title,
                'release_date': release_date,
                'price': price,
                'price_currency': price_currency,
                'developer': developer,
                'publisher': publisher,
                'tags': tags
            }

            print(appid, title)