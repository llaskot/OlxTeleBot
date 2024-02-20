# This is a sample Python script.
# import requests
import time

import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

URL = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/kharkov/?currency=UAH&search%5Border%5D=created_at:desc&view=list'


def parse(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1600,1024")
    # options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.get(url)

    builder = ActionChains(driver)
    elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="l-card"]')
    for elem in elements:
        builder.scroll_to_element(elem).perform()

    page = driver.find_element(By.TAG_NAME, 'html')
    page_content = f'<html>{page.get_attribute("innerHTML")}</html>'
    # driver.close()
    # time.sleep(30)
    return page_content


def assembl(adver: bs4.element.Tag) -> dict:
    return {'info': adver.find('h6').getText(),
            'location_date': adver.find('p', attrs={'data-testid': "location-date"}).getText(),
            'price': adver.find('p', attrs={'data-testid': "ad-price"}).getText(),
            'square': adver.find('span').getText(),
            'link': f"https://www.olx.ua{adver.find('a', href=True).get('href')}",
            'foto': adver.find('img').get('src')
            }


if __name__ == '__main__':
    soup = BeautifulSoup(parse(URL), 'html.parser')
    adv: list[bs4.element.Tag] = soup.find_all("div", attrs={"data-cy": "l-card"})
    content: list[{}] = [assembl(ad) for ad in adv]
    for i in content:
        for j in i:
            print(j, i[j])
        print(' ')
