import csv
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://puritans-pride.in.ua"


class Parser:
    def __init__(self):
        self.base_url = BASE_URL
        self.file = self._open_csv()

    @staticmethod
    def _get(url):
        page = requests.get(url)
        return page

    @staticmethod
    def _open_csv(filename='products.csv'):
        f = csv.writer(open(filename, 'w'))
        f.writerow(['Код товара', 'Название_позиции', 'Поисковые_запросы', 'Описание',
                    'Цена', 'Валюта', 'Ссылка_изображения', 'Продукт на сайте'])
        return f

    def _correct_url(self, url):
        if not url.startswith('http'):
            return self.base_url + url
        return url

    def create_soup(self, url):
        url = self._correct_url(url)
        page = self._get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup

    def parse_category_links(self):
        soup = self.create_soup(self.base_url)
        category_links = []
        li_items = soup.find_all('li', attrs={'class': 'b-nav__item'})

        for li in li_items:
            li_sublinks = li.find_all('a', attrs={'class': 'b-sub-nav__link'})
            if li_sublinks:
                category_links.extend(li_sublinks)
            else:
                li_link = li.find('a', attrs={'class': 'b-nav__link'})
                category_links.append(li_link)

        print(f"Found {len(category_links)} links to product groups pages")

        return category_links

    def parse_product_links(self):
        category_links = self.parse_category_links()
        product_links = []

        for idx, link in enumerate(category_links, 1):
            print(f"Fetching url #{idx}", self._correct_url(link.get('href')))
            soup = self.create_soup(link.get('href'))
            subcategegory_links = soup.find_all('a', attrs={'class': 'b-product-groups-list__image-link'})

            if not subcategegory_links:
                products = soup.find_all('a', attrs={'class': 'b-product-list__image-link'})
                if not products:
                    products = soup.find_all('a', attrs={'class': 'b-product-gallery__image-link'})
                next_page_links = soup.find_all('a', attrs={'class': 'b-pager__link'})
                links = next_page_links[:len(next_page_links) // 2]
                product_links.extend(products)
                print(f"Found {len(products)} link to products")

                if len(links) > 1:
                    links.pop()
                    for idx_x, next_link in enumerate(links, 1):
                        print(f"Fetching next page of url #{idx_x}", self._correct_url(next_link.get('href')))
                        next_page_soup = self.create_soup(next_link.get('href'))
                        products = next_page_soup.find_all('a', attrs={'class': 'b-product-list__image-link'})
                        if not products:
                            products = soup.find_all('a', attrs={'class': 'b-product-gallery__image-link'})
                        product_links.extend(products)
                        print(f"Found {len(products)} link to products")
            else:
                for idx_y, sub_cat_link in enumerate(subcategegory_links):
                    print(f"Fetching sub_url #{idx_y}", self._correct_url(sub_cat_link.get('href')))
                    sub_cat_soup = self.create_soup(sub_cat_link.get('href'))

                    sub_next_page_links = sub_cat_soup.find_all('a', attrs={'class': 'b-pager__link'})
                    sub_links = sub_next_page_links[:len(sub_next_page_links) // 2]

                    products = sub_cat_soup.find_all('a', attrs={'class': 'b-product-gallery__image-link'})
                    if not products:
                        products = soup.find_all('a', attrs={'class': 'b-product-list__image-link'})
                    product_links.extend(products)
                    print(f"Found {len(products)} link to products")

                    if len(sub_links) > 1:
                        sub_links.pop()
                        for next_link in sub_links:
                            print("Fetching url", self._correct_url(next_link.get('href')))
                            next_page_soup = self.create_soup(next_link.get('href'))
                            products = next_page_soup.find_all('a', attrs={'class': 'b-product-gallery__image-link'})
                            if not products:
                                products = soup.find_all('a', attrs={'class': 'b-product-list__image-link'})
                            product_links.extend(products)
                            print(f"Found {len(products)} link to products")

        return product_links

    def write_csv(self):
        links = self.parse_product_links()
        for item in links:
            name = item.contents[0].get('alt')
            link = self._correct_url(item.get('href'))
            self.file.writerow([name, link])
        return True

    @staticmethod
    def get_keywords(soup):
        title = soup.find('meta', attrs={'property': 'og:title'}).get('content')
        first = title.split('.')[0]
        if len(title.split('.')) > 1:
            second = title.split('.')[1].split('&')
            result = (first + '.'.join(second)).replace('"', '').replace('.', ',')
        else:
            result = first
        return result

    def parse_products(self):
        product_links = self.parse_product_links()
        for idx, link in enumerate(product_links):
            l = self._correct_url(link.get('href'))
            print(f"Parsing url #{idx} {l}")
            soup = self.create_soup(link.get('href'))
            product_code = l[len(self.base_url):].split('-')[0][2:]
            product_link = l
            product_name = soup.find('span', attrs={'class': 'b-caption__text'}).contents[0]
            product_keywords = self.get_keywords(soup)
            product_description = soup.find('div', attrs={'class': 'b-tab-list__item'})
            product_price = soup.find('span', attrs={'data-qaid': 'product_price'}).contents[0]
            product_currency = 'UAH'
            product_image = self._correct_url(soup.find('img', attrs={'class': 'b-pictures__img'}).get('src'))
            self.file.writerow([product_code, product_name, product_keywords, product_description,
                                product_price, product_currency, product_image, product_link])

    def parse(self):
        return self.parse_products()


if __name__ == "__main__":
    parser = Parser()
    parser.parse()
