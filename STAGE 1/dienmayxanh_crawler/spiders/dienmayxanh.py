import scrapy


class DienmayxanhSpider(scrapy.Spider):
    name = "dienmayxanh"
    allowed_domains = ["dienmayxanh.com"]

    async def start(self):
        for page in range(16):
            url = (
                "https://www.dienmayxanh.com/Category/"
                f"FilterProductBox?c=1942&o=13&pi={page}"
            )

            yield scrapy.FormRequest(
                url=url,
                method="POST",
                formdata={
                    "IsParentCate": "False",
                    "IsShowCompare": "True",
                    "prevent": "true"
                },
                headers={
                    "Accept": "*/*",
                    "Referer": "https://www.dienmayxanh.com/may-giat",
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": (
                        "application/x-www-form-urlencoded; "
                        "charset=UTF-8"
                    )
                },
                callback=self.parse_product_list
            )

    def parse_product_list(self, response):
        data = response.json()

        print("TONG SAN PHAM THEO API:", data.get("total"))

        html = data.get("listproducts", "")

        if not html:
            return

        selector = scrapy.Selector(text=html)

        links = selector.css("a::attr(href)").getall()

        product_urls = set()

        for link in links:
            if link and link.startswith("/tivi/"):
                url = response.urljoin(link.split("?")[0])
                product_urls.add(url)

        print("SO LINK SAN PHAM:", len(product_urls))

        for url in product_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_product
            )

    def parse_product(self, response):
        html = response.text

        # Tên sản phẩm
        product_name = response.css("h1::text").get()

        # Giá bán
        key = '"SalePriceVat":'
        pos = html.find(key)

        sale_price = None

        if pos != -1:
            start = pos + len(key)
            end = html.find(",", start)
            sale_price = html[start:end]

        # Thuộc tính sản phẩm
        specs = {}
        pos = 0

        while True:
            pos = html.find(
                '"@type":"PropertyValue"',
                pos
            )

            if pos == -1:
                break

            section = html[pos:pos + 500]

            name_start = section.find('"name":"')
            value_start = section.find('"value":"')

            if name_start != -1 and value_start != -1:
                name_start += len('"name":"')
                name_end = section.find(
                    '"',
                    name_start
                )

                value_start += len('"value":"')
                value_end = section.find(
                    '"',
                    value_start
                )

                attr_name = section[
                    name_start:name_end
                ]

                attr_value = section[
                    value_start:value_end
                ]

                specs[attr_name] = attr_value

            pos += 30

        # Xuất dữ liệu
        yield {
            "product_name": product_name,
            "sale_price": sale_price,
            "tv_type": specs.get("Loại Tivi"),
            "screen_size": specs.get("Kích cỡ màn hình"),
            "resolution": specs.get("Độ phân giải"),
            "screen_type": specs.get("Loại màn hình"),
            "operating_system": specs.get("Hệ điều hành"),
            "ram": specs.get("RAM"),
            "rom": specs.get("ROM (Bộ nhớ lưu trữ)"),
            "release_year": specs.get("Năm ra mắt")
        }