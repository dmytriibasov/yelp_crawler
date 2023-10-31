import json

import scrapy


class YelpSpider(scrapy.Spider):
    name = "yelp_crawler"
    allow_domains = ["yelp.com"]
    start_urls = ["https://www.yelp.com/"]
    base_url = 'https://www.yelp.com/search?find_desc={}&find_loc={}'

    def __init__(self, location, category, file_path=None, *args, **kwargs):
        super(YelpSpider, self).__init__(*args, **kwargs)
        self.location = location
        self.category = category
        self.file_path = self._set_file_path(file_path)

    def _set_file_path(self, file_path):

        if file_path is None:
            file_path = f"{self.category}-{self.location}_data.json"
        return file_path

    def start_requests(self):

        start_url = self.base_url.format(self.category, self.location)
        yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response, **kwargs):

        for business in response.css('h3 span a'):
            business_link = business.css('::attr(href)').get()  # Extract yelp business link

            business_url = response.urljoin(business_link)  # Build the URL for the detailed business page
            yield scrapy.Request(url=business_url, callback=self.parse_business)

        # To proceed with paginated objects. Uncomment if necessary
        # next_page = response.css('a.next-link::attr(href)').get()
        #
        # if next_page:
        #     yield response.follow(next_page, callback=self.parse)

    def parse_business(self, response):
        """To parse Yelp business detailed page"""

        yelp_biz_id = response.css('meta[name="yelp-biz-id"]::attr(content)').get()  # yelp business_id
        business_rating = response.css('span.css-1p9ibgf::text').get()
        business_website_div = response.xpath('//div[p[contains(text(), "Business website")]]')
        business_website = business_website_div.css('p.css-1p9ibgf a.css-1idmmu3::text').get()

        ajax_url = f"https://www.yelp.com/biz/{yelp_biz_id}/props"

        yield scrapy.Request(url=ajax_url, callback=self.parse_ajax,
                             cb_kwargs={
                                 "business_yelp_url": response.url,
                                 "business_rating": business_rating,
                                 "business_website_from_html": business_website}
                             )

    def parse_ajax(self, response, **kwargs):
        """To parse Ajax response data"""
        ajax_data = response.json().get("bizDetailsPageProps", {})

        business_name = ajax_data.get("businessName")
        reviews_data = ajax_data.get("reviewFeedQueryProps")
        number_of_reviews = reviews_data.get("pagination", {}).get("totalResults")
        business_website_from_ajax = reviews_data.get("bizPortfolioProps", {}).get("ctaProps", {}).get("website")

        reviews = []
        for item in reviews_data.get("reviews", [])[:5]:
            review_date = item.get("localizedDate")
            reviewer_name = item.get("user", {}).get("markupDisplayName")
            reviewer_location = item.get("user", {}).get("displayLocation")
            reviews.append(
                {"Reviewer Name": reviewer_name, "Reviewer Location": reviewer_location, "Review Date": review_date}
            )

        business_data = {
            'Business Name': business_name,
            'Business Rating': str(kwargs.get("business_rating")),
            'Number of Reviews': number_of_reviews,
            'Business Yelp url': str(kwargs.get("business_yelp_url")),
            'Business Website': business_website_from_ajax or kwargs.get("business_website_from_html"),
            'Reviews': reviews
        }

        self._write_into_json(data=business_data)

    def _write_into_json(self, data):

        with open(self.file_path, "a", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False)
            json_file.write("\n")
