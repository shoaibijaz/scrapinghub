# -*- coding: utf-8 -*-
import scrapy
import math
from artworks.items import ArtworksItem


class ArtworkSpider(scrapy.Spider):
    name = 'art'
    start_urls = ["http://pstrial-2019-12-16.toscrape.com/browse/"]

    def parse(self, response):

        # this will check the total products to count the page
        xp_page_count = "//label[@class='item-count']/text()"
        pages = response.xpath(xp_page_count).extract_first()
        ref_url = response.url

        if pages:
            page_count_text = pages.replace('items', '').strip()
            pages_count = math.floor(int(page_count_text)/10)

            for page in range(0, pages_count):
                url = ref_url + '?page='+str(page)
                url = response.urljoin(url)
                yield scrapy.Request(url, callback=self.crawl_items)

        urls_list = response.xpath("//div[@id='subcats']//a/@href")
        if len(urls_list) > 0:
            for href in urls_list:
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.parse)

    # function will crawl the artwork links
    def crawl_items(self, response):
        urls_list = response.xpath("//a[contains(@href,'item')]/@href")
        if len(urls_list) > 0:
            for href in urls_list:
                url = response.urljoin(href.extract())
                yield scrapy.Request(url, callback=self.crawl_item)

    # function will crawl the details
    def crawl_item(self, response):
        item = ArtworksItem()
        item['url'] = response.url
        title_xp = "//div[@id='content']//h1/text()"
        title_node = response.xpath(title_xp).extract_first()

        if title_node is not None:
            item['title'] = title_node
        img_xp = "//div[@id='body']//img/@src"
        img_node = response.xpath(img_xp).extract_first()

        if img_node is not None:
            item['image'] = img_node
        art_xp = "//div[@id='content']//h2[@class='artist']/text()"
        artist_node = response.xpath(art_xp).extract_first()

        if artist_node is not None:
            item['artist'] = artist_node
        desc_xp = "//div[@id='content']//div[@class='description']/text()"
        description_node = response.xpath(desc_xp).extract_first(desc_xp)
        if description_node is not None:
            item['description'] = description_node
        cat_xp = "//div[@id='content']//a[1]/@href"
        categories_node = response.xpath(cat_xp).extract_first()

        if categories_node is not None:
            item['categories'] = categories_node

        dim_xp = "//td[@class='key' and contains(text(),'Dimensions')]/parent::tr/td[@class='value']/text()"
        dim_node = response.xpath(dim_xp).extract_first()

        if dim_node is not None:
            dimens_keys = dim_node.split('x')
            item['width'] = dimens_keys[0].strip()

            if len(dimens_keys) > 1:
                item['height'] = dimens_keys[1].split('in')[0].strip()

        return item
