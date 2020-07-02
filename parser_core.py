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

    def _open_csv(self, filename='products.csv'):
        f =  csv.writer(open(filename, 'w'))
        f.writerow(['Name', 'Link'])
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

        for link in category_links:
            print("Fetching url", self._correct_url(link.get('href')))
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
                    for next_link in links:
                        print("Fetching url", self._correct_url(next_link.get('href')))
                        next_page_soup = self.create_soup(next_link.get('href'))
                        products = next_page_soup.find_all('a', attrs={'class': 'b-product-list__image-link'})
                        if not products:
                            products = soup.find_all('a', attrs={'class': 'b-product-gallery__image-link'})
                        product_links.extend(products)
                        print(f"Found {len(products)} link to products")
            else:
                for sub_cat_link in subcategegory_links:
                    print("Fetching url", self._correct_url(sub_cat_link.get('href')))
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

    def parse(self):
        return self.write_csv()


if __name__ == "__main__":
    parser = Parser()
    parser.parse()
