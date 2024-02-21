# from bot.user_data import UserData
import re

import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By


cities_ru = ["Харьков", "Киев", "Львов", "Винница", "Днепр", "Житомир", "Запорожье", "Ивано-Франковск",
             "Кропивницкий", "Луцк", "Николаев", "Одесса", "Полтава", "Ровно", "Сумы", "Тернополь", "Ужгород",
             "Херсон", "Черкассы", "Хмельницкий", "Чернигов", "Черновцы"]

cities_en = ["kharkov", "kiev", "lvov", "vinnitsa", "dnepr", "zhitomir", "zaporozhe", "ivano-frankovsk",
             "kropivnitskiy", "lutsk", "nikolaev_106", "odessa", "poltava", "rovno", "sumy", "ternopol", "uzhgorod",
             "kherson", "cherkassy", "khmelnitskiy", "chernigov", "chernovtsy"]

rooms = {
    1: 'search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=odnokomnatnye&',
    2: 'search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=dvuhkomnatnye&',
    3: 'search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=trehkomnatnye&',
    4: 'search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=chetyrehkomnatnye&',
    5: 'search%5Bfilter_enum_number_of_rooms_string%5D%5B0%5D=pyatikomnatnye&'
}


class Parser:
    def __init__(self, info):
        self.city = info.selected_city
        self.min_rooms = info.min_rooms
        self.max_rooms = info.max_rooms
        self.min_price = info.min_price
        self.max_price = info.max_price

    def selected_city(self) -> str:
        try:
            index = cities_ru.index(self.city)
            return cities_en[index]
        except ValueError:
            return None

    def get_rooms(self):
        if self.min_rooms == self.max_rooms:
            return rooms[self.min_rooms]
        elif self.min_rooms == 1 and self.max_rooms == 5:
            return ''
        else:
            all_rooms: str = ''
            for i, num in enumerate(range(self.min_rooms, self.max_rooms + 1)):
                all_rooms += rooms[num].replace('enum_number_of_rooms_string%5D%5B0%5D'
                                                , f'enum_number_of_rooms_string%5D%5B{i}%5D')
            return all_rooms

    def get_price(self) -> str:
        price: str = ''
        min_p = f'search%5Bfilter_float_price:from%5D={self.min_price}&'
        max_p = f'search%5Bfilter_float_price:to%5D={self.max_price}&'
        if self.min_price > 0:
            price += min_p
        if self.max_price > 0:
            price += max_p
        return price

    def get_url(self):
        return (
            f'https://www.olx.ua/uk/nedvizhimost/kvartiry/dolgosrochnaya-arenda-kvartir/{self.selected_city()}/?currency=UAH'
            f'&search%5Border%5D=created_at:desc&{self.get_price()}{self.get_rooms()}view=list')

    def parse(self, url):
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1600,1024")
        options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        driver.get(url)

        builder = ActionChains(driver)
        elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="l-card"]')
        for elem in elements:
            builder.scroll_to_element(elem).perform()

        page = driver.find_element(By.TAG_NAME, 'html')
        page_content = f'<html>{page.get_attribute("innerHTML")}</html>'
        # time.sleep(30)
        driver.close()
        driver.quit()
        return page_content

    def assembl(self, adver: bs4.element.Tag) -> dict:
        return {'info': adver.find('h6').getText(),
                'location_date': adver.find('p', attrs={'data-testid': 'location-date'}).getText(),
                'price': adver.find('p', attrs={'data-testid': 'ad-price'}).getText(),
                'square': adver.find('span').getText(),
                'link': f"https://www.olx.ua{adver.find('a', href=True).get('href')}",
                'foto': adver.find('img').get('src'),
                'paid': False if adver.find('div', attrs={'data-testid': 'adCard-featured'}) is None else True
                }

    def get_advertising(self):
        url = self.get_url()
        print(url)
        soup = BeautifulSoup(self.parse(url), 'html.parser')



        advertisements_qty = soup.find('span', attrs={'data-testid': 'total-count'}).getText()
        digits = re.findall(r'\d', advertisements_qty)
        res = int(''.join(digits))
        print('advertisements_qty = ', res)

        further = soup.find('p', string='Подивіться результати для більшої відстані:')
        # print('further = ', further)
        adv = []
        if further is None:
            adv = soup.find_all("div", attrs={"data-cy": "l-card"})
        else:
            adv = further.find_all_previous("div", attrs={"data-cy": "l-card"})
            adv.reverse()
        content: list[{}] = [self.assembl(ad) for ad in adv]





        # adv: list[bs4.element.Tag] = soup.find_all('div', attrs={'data-cy': 'l-card'})
        # content: list[{}] = [self.assembl(ad) for ad in adv]
        # print(content[4])
        return res, content

# if __name__ == '__main__':
#     min_rooms = 2
#     max_rooms = 5
#
#
#
#     def get_rooms():
#         print(rooms[min_rooms])
#         if min_rooms == max_rooms:
#             print(rooms[min_rooms])
#             return rooms[min_rooms]
#
#         else:
#             all_rooms : str = ''
#             for i, num in enumerate(range(min_rooms, max_rooms)):
#                 all_rooms += rooms[num].replace('enum_number_of_rooms_string%5D%5B0%5D'
#                                               , f'enum_number_of_rooms_string%5D%5B{i}%5D')
#                 print('i = ', i)
#                 print('num = ', num)
#                 print('all_rooms = ', all_rooms )
#
#             return all_rooms
#
#     get_rooms()
