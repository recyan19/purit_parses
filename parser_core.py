import time
import csv
import requests
from bs4 import BeautifulSoup


BASE_URL = "http://puritans-pride.in.ua"

page = requests.get(BASE_URL)
soup = BeautifulSoup(page.text, 'html.parser')


f = csv.writer(open('prod_links.csv', 'w'))
f.writerow(['Name', 'Link'])


category_links = []
li_items = soup.find_all('li', attrs={'class': 'b-nav__item'})
print("Found base category links.\n")
for li in li_items:
    li_sublinks = li.find_all('a', attrs={'class': 'b-sub-nav__link'})
    if li_sublinks:
        category_links.extend(li_sublinks)
    else:
        li_link = li.find('a', attrs={'class': 'b-nav__link'})
        category_links.append(li_link)


product_links = []


for link in category_links:
    page = ''
    while page == '':
        try:
            url = BASE_URL + link.get('href') + "?view_as=list"
            print("url", url)
            page = requests.get(url)
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue

    soup = BeautifulSoup(page.text, 'html.parser')

    subcategegory_links = soup.find_all('a', attrs={'class': 'b-product-list__image-link'})

    if not subcategegory_links:
        products = soup.find_all('a', attrs={'class': 'b-product-list__image-link'})
        product_links.extend(products)
        print("Found link to products", '\n'.join(products))
    else:
        for sub_cat_link in subcategegory_links:
            sub_cat_page = ''
            while sub_cat_page == '':
                try:
                    sub_cat_page = requests.get(BASE_URL + sub_cat_link.get('href') + "?view_as=list")
                    break
                except:
                    print("Connection refused by the server..")
                    print("Let me sleep for 5 seconds")
                    print("ZZzzzz...")
                    time.sleep(5)
                    print("Was a nice sleep, now let me continue...")
                    continue

            sub_cat_soup = BeautifulSoup(sub_cat_page.text, 'html.parser')
            products = sub_cat_soup.find_all('a', attrs={'class': 'b-product-list__image-link'})
            product_links.extend(products)
            print("Found link to products", '\n'.join(products))


for item in product_links:
    name = item.contents[0]
    link = BASE_URL + item.get('href')

    f.writerow([name, link])
