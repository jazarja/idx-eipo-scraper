import json
import scrapy
import html
from scrapy.http import HtmlResponse
from urllib.parse import urljoin


class IpoSpider(scrapy.Spider):
    name = "ipo"
    root_url = "https://e-ipo.co.id"

    flare_solver_url = "http://localhost:8191/v1"
    start_urls = ["https://e-ipo.co.id/id/ipo/index"]

    def start_requests(self):
        for url in self.start_urls:
            payload = {
                "cmd": "request.get",
                "url": url,
                "maxTimeout": 60000
            }
            yield scrapy.Request(self.flare_solver_url, method='POST',
                                 body=json.dumps(payload),
                                 headers={'Content-Type': 'application/json'})

    def parse(self, response):
        current_url = json.loads(response.request.body)['url']
        if "ipo/index" in current_url:
            # Parse the IPO page layout
            for item in self.parse_index_page(response):
                yield item
        else:
            # Parse the other page layout
            for item in self.parse_detail_page(response):
                yield item

    def parse_detail_page(self, response):
        print("Parse detail page:" + json.loads(response.request.body)['url'])

        company_name = response.xpath("//h1[contains(@class, 'panel-title')]/text()").get()
        code = response.xpath("//h5[contains(text(), 'Kode Emiten')]/following-sibling::p/text()").get()
        sector = response.xpath("//h5[contains(text(), 'Sektor')]/following-sibling::p/text()").get()
        subsector = response.xpath("//h5[contains(text(), 'Subsektor')]/following-sibling::p/text()").get()
        lines_of_business  = response.xpath("//h5[contains(text(), 'Bidang usaha')]/following-sibling::p/text()").get()
        summary = response.xpath(
            "//h5[contains(text(), 'Ringkasan Perusahaan Emiten')]/following-sibling::p/text()").get()
        address = response.xpath("//h5[contains(text(), 'Alamat')]/following-sibling::p/text()").get()
        website = response.xpath("//h5[contains(text(), 'Situs Perusahaan Emiten')]/following-sibling::p/a/@href").get()
        shares_offered = response.xpath(
            "//h5[contains(text(), 'Jumlah Saham Ditawarkan')]/following-sibling::p/text()").get()
        percent_total_shares = response.xpath(
            "//h5[contains(text(), '% dari Total Saham Dicatatkan')]/following-sibling::p/text()").get()
        admin_participant = response.xpath("//h5[contains(text(), 'Partisipan Admin')]/following-sibling::p/text()").get()

        underwriters = response.xpath("//h5[contains(text(), 'Penjamin Emisi')]/following-sibling::p/text()").getall()

        underwriter = ', '.join(underwriters)

        book_building_date = response.xpath("//h5[contains(text(), 'Book Building')]/following-sibling::p/text()").get()

        book_building_price = response.xpath("//h5[contains(text(), 'Book Building')]/following-sibling::p[2]/text()").get()

        pooling_date = response.xpath("//h5[contains(text(), 'Penawaran Umum')]/following-sibling::p/text()").get()

        pooling_price = response.xpath("//h5[contains(text(), 'Penawaran Umum')]/following-sibling::p[2]/text()").get()

        distribution_date = response.xpath("//h5[contains(text(), 'Distribusi')]/following-sibling::p/text()").get()

        listing_date = response.xpath("//h5[contains(text(), 'Tanggal Pencatatan')]/following-sibling::p/text()").get()


        data = {
            "company_name": company_name,
            "code": code,
            "sector": sector,
            "subsector": subsector,
            "lines_of_business" : lines_of_business,
            "summary": summary,
            "address": address,
            "website": website,
            "shares_offered": shares_offered,
            "percent_total_shares": percent_total_shares,
            "underwriter": underwriter,
            "admin_participant" : admin_participant,
            "book_building_date" : book_building_date,
            "pooling_date" : pooling_date,
            "distribution_date" : distribution_date,
            "listing_date" : listing_date,
            "book_building_price" : book_building_price,
            "pooling_price" : pooling_price,

        }

        # Return the dictionary
        yield data

    def parse_index_page(self, response):
        print("Parsing index page")
        data = json.loads(response.body)

        # Extract IPO information
        response = HtmlResponse(url=json.loads(response.request.body)['url'], body=data['solution']['response'],
                                encoding="utf-8")

        for box in response.css(".pricing-box"):
            ipo_info = {}

            ipo_info['offering'] = box.css('div.pricing-title h3::text').get()
            ipo_info['logo'] = urljoin(self.root_url, box.css('img.img-list::attr(src)').get())
            ipo_info['company'] = box.css('div.padding5 h5::text').get()
            ipo_info['sector'] = box.css('div.pricing-features ul li:nth-child(1) p::text').get()
            ipo_info['offering_period'] = html.unescape(
                box.css('div.pricing-features ul li:nth-child(2) p::text').get())
            ipo_info['offering_price'] = html.unescape(box.css('div.pricing-features ul li:nth-child(3) p::text').get())
            ipo_info['shares_offered'] = box.css('div.pricing-features ul li:nth-child(4) p::text').get()
            ipo_info['prospectus_url'] = urljoin(self.root_url,
                                                 box.css('div.pricing-features ul li:nth-child(5) a::attr(href)').get())
            ipo_info['additional_info_url'] = urljoin(self.root_url, box.css(
                'ddiv.pricing-features ul li:nth-child(6) a::attr(href)').get())
            ipo_info['more_info_url'] = urljoin(self.root_url, box.css('div.pricing-action a::attr(href)').get())

            #yield ipo_info
            payload = {
                "cmd": "request.get",
                "url": ipo_info['more_info_url'],
                "maxTimeout": 60000
            }
            yield scrapy.Request(self.flare_solver_url, method='POST',
                                 body=json.dumps(payload),
                                 headers={'Content-Type': 'application/json'})



        # Follow pagination links
        active_page = response.css(".pagination li.active a::attr(data-page)").get()

        # Extract the pagination links container
        pagination = response.css(".pagination")

        # Find the next link after the active one
        next_link = pagination.css(f'li a[data-page="{int(active_page) + 1}"]::attr(href)').get()

        if next_link:
            full_next_url = urljoin(self.root_url, next_link)
            payload = {
                "cmd": "request.get",
                "url": full_next_url,
                "maxTimeout": 60000
            }
            yield scrapy.Request(self.flare_solver_url, method='POST',
                                 body=json.dumps(payload),
                                 headers={'Content-Type': 'application/json'})


