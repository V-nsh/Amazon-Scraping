from bs4 import BeautifulSoup
import pandas as pd
import requests
from fake_useragent import UserAgent
import re

def get_soup_retry(url):
    ua = UserAgent()
    uag_random = ua.random

    header = {
        'User-Agent': uag_random,
        'Accept-Language': 'en-US,en;q=0.9'
    }
    isCaptcha = True
    while isCaptcha:
        page = requests.get(url, headers=header)
        if page.status_code != 200:
            print(f'Request to {url} failed with status code: {page.status_code}')
            return None
        soup = BeautifulSoup(page.content, 'lxml')
        if 'captcha' in str(soup):
            uag_random = ua.random
            print(f'\rBot has been detected... retrying ... use new identity: {uag_random} ', end='', flush=True)
            continue
        else:
            print('Bot bypassed')
            return soup
        
def remove_white_spaces(text):
    text =  re.sub(r'\s', '', text)
    return text
        
df =  pd.read_csv("table.csv")
urls = df['URL'].tolist()[:200]
smdict = None
data_list = None
complete_df = pd.DataFrame()

for url in urls:
    bs = get_soup_retry(url)
    if bs is None:
        continue
    htm = bs.prettify()
    with open("bagpg.html","w", encoding="utf-8") as file: # saving html file to disk
        file.write(htm)
    pdTable = bs.find('table', {'id':'productDetails_detailBullets_sections1'})
    techTable = bs.find('table', {'id':'productDetails_techSpec_section_1'})

    data = {
        'Description': [],
        'ASIN': [],
        'Product Description': [],
        'Manufacturer': []
    }

    asin = ''
    asinp = ''
    manup = ''
    manu = ''
    if pdTable:
        asin = pdTable.find('th', {'class': 'a-color-secondary a-size-base prodDetSectionEntry'})
    else:
        details =  bs.find('div', id='detailBulletsWrapper_feature_div')
        # print(details.prettify())
        if details:
            span_tags = details.find_all('span', {'class': 'a-text-bold'})
            # print(span_tags)
            if span_tags:
                smdict = {}
                for spans in span_tags:
                    label = spans.text.strip()
                    label = remove_white_spaces(label)
                    val = spans.find_next_sibling().text
                    smdict[label] = val

                clean_dict = {}
                prefixes = ['Manufacturer', 'ASIN']
                for key, value in smdict.items():
                    if key.startswith(tuple(prefixes)):
                        clean_key = key.replace('\u200f:\u200e', '')
                        clean_dict[clean_key] = value
                manup = clean_dict.get('Manufacturer')
                asinp = clean_dict.get('ASIN')
    if asin:
        asin = asin.find_next_sibling('td').text.strip()
    if techTable:
        manu = techTable.find('th', {'class': 'a-color-secondary a-size-base prodDetSectionEntry'})
    if manu:
        manu = manu.find_next_sibling('td').text.strip()

    if asinp:
        data['ASIN'].append(asinp)
    elif asin:
        data['ASIN'].append(asin)
    else:
        data['ASIN'].append('')

    if manup:
        data['Manufacturer'].append(manup)
    elif manu:
        data['Manufacturer'].append(manu)
    else:
        data['Manufacturer'].append('')

    des = bs.find('div', {'id': 'feature-bullets'})
    if des:
        fdes = des.find_all('span', {'class': 'a-list-item'})
    if fdes:
        desList = []
        for i in fdes:
            desList.append(i.text.strip())

    pdesc = bs.find('div', {'id': 'detailBulletsWrapper_feature_div'})
    
    pdesc1 = bs.find('div', {'id': 'aplus_feature_div'})

    target_h2 = bs.find('h2', text='Product Description')

    next_element = None
    text = None
    im = None
    if target_h2:
        # Get the next sibling element
        next_element = target_h2.find_next_sibling()
    elif smdict:
        clean_dict = {}
        for key, value in smdict.items():
            clean_key = key.replace('\u200f:\u200e', '')
            clean_dict[clean_key] = value

        data_list = list(clean_dict.items())

    if next_element:
        # Get the text of the next element
        text = next_element.find_all('div', {'class': 'apm-eventhirdcol apm-floatleft'})
        p = next_element.find_all('p')
        # print('text:', text)
        # print('p:',p)
    # plist = []
    # if p:
    #     for i in p:
    #         plist.append(i.text.strip())

    plist = []
    if text:
        for i in text:
            im = i.find_all('img')
            if im:
                # for j in im:
                #     sr = j.get('data-src')
                #     if sr:
                #         print(sr)
                #         plist.append(sr)
                #     else:
                #         continue  
                continue 
            plist.append(i.text.strip())
    if desList:
        data['Description'].append(desList)
    else:
        data['Description'].append('')
        
    if plist:
        data['Product Description'].append(plist)
    elif data_list:
        data['Product Description'].append(data_list)
    else:
        data['Product Description'].append('')

    df = pd.DataFrame(data)
    # df['Description'] = df['Description'].apply(lambda x: ', '.join(map(str, x)))
    # df['Product Description'] = df['Product Description'].apply(lambda x: ', '.join(map(str, x)))

    complete_df = complete_df.append(df, ignore_index=True)

complete_df.to_csv('task2.csv', index=False)