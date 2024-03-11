# This is a sample Python script.
# import requests
import time

import bs4
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

URL = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/nikolaev_106/?currency=UAH&search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=odnokomnatnye&search%5Bfilter_enum_number_of_rooms_string%5D%5B1%5D=dvuhkomnatnye&search%5Bfilter_enum_number_of_rooms_string%5D%5B2%5D=trehkomnatnye&search%5Bfilter_float_price%3Afrom%5D=1500&search%5Bfilter_float_price%3Ato%5D=5000&search%5Border%5D=created_at%3Adesc&view=list'


def parse(url):
    docker_selenium_server = 'http://127.0.0.1:4444'
    options = webdriver.ChromeOptions()
    # options.add_argument("--window-size=1600,1024")
    # options.add_argument("--headless")

    # driver = webdriver.Chrome(options=options)
    driver = webdriver.Remote(command_executor=docker_selenium_server, options=options)
    driver.implicitly_wait(5)
    driver.get(url)

    builder = ActionChains(driver)
    elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="l-card"]')
    for elem in elements:
        builder.scroll_to_element(elem).perform()

    page = driver.find_element(By.TAG_NAME, 'html')
    page_content = f'<html>{page.get_attribute("innerHTML")}</html>'
    driver.close()
    driver.quit()
    # time.sleep(30)
    return page_content


# def check_number(number:)

def assembl(adver) -> dict:

    return {'info': adver.find('h6').getText(),
            'location_date': adver.find('p', attrs={'data-testid': "location-date"}).getText(),
            'price': adver.find('p', attrs={'data-testid': "ad-price"}).getText(),
            'square': adver.find('span').getText(),
            'link': f"https://www.olx.ua{adver.find('a', href=True).get('href')}",
            'foto': adver.find('img').get('src'),
            'paid': False if adver.find('div', attrs={'data-testid': 'adCard-featured'}) is None else True
            }


if __name__ == '__main__':
    soup = BeautifulSoup(parse(URL), 'html.parser')

    further = soup.find('p', string='Подивіться результати для більшої відстані:')
    # print('further = ', further)
    adv = []
    if further is None:
        adv = soup.find_all("div", attrs={"data-cy": "l-card"})
    else:
        adv = further.find_all_previous("div", attrs={"data-cy": "l-card"})
        adv.reverse()
    content: list[{}] = [assembl(ad) for ad in adv]
    for i in content:
        for j in i:
            print(j, i[j])
        print(' ')
