from bs4 import BeautifulSoup
import pandas as pd
import requests

url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"

headers = {
    'authority': 'www.amazon.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}
count = 0

def scrapeURL(url):
    global count
    response = requests.get(f"{url}", headers=headers)

    with open("webpg.html","w", encoding="utf-8") as file: # saving html file to disk
        file.write(response.text)

    bs = BeautifulSoup(response.text, "html.parser")
    items = bs.select("div[data-component-type='s-search-result']")
    data = {
        'URL': [],
        'Name': [],
        'Price': [],
        'Rating': [],
        'Reviews': []
    }
    for item in items:
        link_element = item.find('a', {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
        if link_element:
            link = "https://www.amazon.in" + link_element.get('href')
            data['URL'].append(link)

            name_element = item.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
            if name_element:
                name = name_element.text.strip()
                data['Name'].append(name)
            else:
                data['Name'].append('')

            price_element = item.find('span', {'class': 'a-price-whole'})
            if price_element:
                price = price_element.text.strip()
                data['Price'].append(price)
            else:
                data['Price'].append('')

            rating_element = item.find('span', {'class': 'a-icon-alt'})
            if rating_element:
                rating = rating_element.text.strip()
                data['Rating'].append(rating)
            else:
                data['Rating'].append('')

            review_element = item.find('span', {'class': 'a-size-base s-underline-text'})
            if review_element:
                review = review_element.text.strip()
                data['Reviews'].append(review)
            else:
                data['Reviews'].append('')
    table =  pd.DataFrame(data)
    # table.to_csv("table.csv", sep=',', encoding='utf-8')
    return [table, bs]

def scrapeLimit(url, len):
    data = pd.DataFrame()
    for page in range(len):
        small = scrapeURL(url)
        data = pd.concat([data, small[0]], ignore_index=True)
        print(data)
        url = small[1].find('a', {'class': 's-pagination-item s-pagination-next s-pagination-button s-pagination-separator'})
        # url = url[0].get('href')
        print('url:', url)
        if url:
            url = url.get('href')
            url = "https://www.amazon.in" + url
            print(url)
        else:
            break
    data.to_csv("table.csv", sep=',', encoding='utf-8')

scrapeLimit(url, 20)