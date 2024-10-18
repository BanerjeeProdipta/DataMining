from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

priceDict = {}

driver = webdriver.Chrome()

productName = input("Enter the product's name: ")

with tqdm(total=3, desc="Fetching prices", bar_format='{l_bar}{bar} [Elapsed: {elapsed}]') as pbar:
    url = "https://www.bestbuy.ca/en-ca/search?search=" + productName


    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    fullContent = soup.find('div',{'class','productsRow_DcaXn style-module_row__Q0c-x'}).findAll('div')[0]
    name = fullContent.find('div',{"itemprop" :'name'}).getText()
    price = fullContent.find('span',{"data-automation" :'product-price'}).find('span').getText()
    
    pbar.update(1)

    url1 = 'https://www.amazon.ca/s?k=' + productName

    driver.get(url1)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    fullContent = soup.find('div',{'cel_widget_id':'MAIN-SEARCH_RESULTS-3'})
    name1 = fullContent.find('span',{'class':'a-size-base-plus a-color-base a-text-normal'}).getText()
    price1 = fullContent.find('span',{'class':'a-price'}).find('span').getText()
    
    pbar.update(1)


    url2 = "https://www.ebay.ca/"

    driver.get(url2)

    elementID = driver.find_element(By.NAME, "_nkw")
    elementID.send_keys(productName)
    elementID.submit()

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    fullContent = soup.find('ul',{'class','srp-results srp-list clearfix'}).findAll('li')[1]
    name2 = fullContent.find('div',{"class" :'s-item__title'}).getText()
    price2 = fullContent.find('span',{"class" :'s-item__price'}).find('span').getText()
    
    pbar.update(1)

    price =  price[1:]
    price1 = price1[1:]
    price2 = price2[3:]

    priceDict['Best Buy'] = float(price)
    priceDict['Amazon'] = float(price1)
    priceDict['Ebay'] = float(price2)




    print("\nBest Buy")
    print(name + " : " + price)
    print("\nAmazon")
    print(name1 + " : " + price1)
    print("\nEbay")
    print(name2 + " : " + price2)


    for key, value in priceDict.items():
        if value == min(priceDict.values()):
            print(f"\n\nIn {key}, The price of {productName} is cheaper with price ${value}")
            break

