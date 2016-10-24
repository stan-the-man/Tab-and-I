import scrapy
import re
from tutorial.items import TabItem


# what it do with this segment of the project?
# [] need to put the information into a DB that allows me to access
# [] need to test how well it functions.
# [] are there any unit tests I can write?


class tabSpider(scrapy.Spider):
    name = 'tabs'
    allowed_domains = ['ultimate-guitar.com']
    start_urls = [
        'https://tabs.ultimate-guitar.com/m/metallica/nothing_else_matters_tab.htm',
        'https://tabs.ultimate-guitar.com/l/led_zeppelin/stairway_to_heaven_tab.htm'
    ]

    def parse(self, response):
        item = TabItem()
        item['tuning'] = "Standard"
        item['capo'] = "No Capo"
        item['tab'] = response.xpath('//pre[@class="js-tab-content"]').extract()
        title = response.xpath('//title/text()').extract()[0]
        item['song'] = re.search('.*?(?= TAB)', title).group(0).lower()
        item['artist'] = re.search('(?<=by ).*?(?= @)', title).group(0).lower()
        item['tab_author'] = response.xpath('//div[@class="t_dtde"]/a/@href').extract()

        if response.xpath('//div[@class="t_dt"]').re('Tuning'):
            t_dtde = response.xpath('//div[@class="t_dtde"]/text()').extract()
            item['tuning'] = self.clean_info(t_dtde)

        if response.xpath('//div[@class="t_dt"]').re('Capo'):
            t_dtde = response.xpath('//div[@class="t_dtde"]/text()').extract()
            item['capo'] = self.clean_info(t_dtde)
        yield item

    def clean_info(self, inp):
        return [re.sub('\s', '', str(thing)) for thing in inp if re.sub('\s', '', str(thing)) != '']
