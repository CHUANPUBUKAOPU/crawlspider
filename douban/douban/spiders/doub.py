# import scrapy
from scrapy_redis.spiders import RedisSpider
from douban.items import DoubanItem
from scrapy.http import Request

class DoubSpider(RedisSpider):
    name = "doub"
    # allowed_domains = ["douban.com"]
    # start_urls = ["http://douban.com/"]
    redis_key='1'
    # 控制爬取的页数
    page=0
    def parse(self, response):
        info = response.xpath('//div[@class="info"]')
        for i in info:
            title = i.xpath('./div/a/span[1]/text()').extract()[0]
            director = i.xpath('./div/p/text()').extract()[0].strip()
            score = i.xpath('.//div/span[2]/text()').extract()[0]
            quote = i.xpath('.//div/p/span/text()').extract()[0]
            detail_url = i.xpath('./div/a/@href').extract()[0]

            item = DoubanItem()
            item['title'] = title
            item['director'] = director
            item['score'] = score
            item['quote'] = quote

            yield Request(detail_url,callback=self.get_detail,meta={'info':item})
        
        # 上一次请求是第几页
        if response.meta.get('num'):
            self.page = response.meta['num']
        self.page += 1
        if self.page == 2: # 只爬前两页
            return
        page_url='https://movie.douban.com/top250?start={}&filter='.format(self.page*25)
        yield Request(page_url,meta={'num':self.page})

    def get_detail(self,response):
        items = DoubanItem()
        info = response.meta['info']
        items.update(info)
        detail = response.xpath('//span[@property="v:summary"]/text()').extract()[0].strip()
        items['detail'] = detail
        yield items