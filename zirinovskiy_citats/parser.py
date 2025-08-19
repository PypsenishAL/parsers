import requests
from fake_useragent import UserAgent
import json
from time import time
from time import sleep
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# from parser_selenium_likes import massive_of_likes

start = time()
headers = {'user-agent': UserAgent().random}
data = []

for i in tqdm(range(1, 3)):
    url = f'https://ru.citaty.net/avtory/vladimir-volfovich-zhirinovskii/?page={i}'
    try:
        response = requests.get(url=url, timeout=(3, 3), headers=headers)
        response.encoding = 'utf-8'
        response.raise_for_status()
        if response.status_code != 200:
            raise requests.exceptions.RequestException
        else:
            print(f'Успешный запрос к {i} странице : {response.reason}')
    except requests.exceptions.RequestException as error:
        print(f'Ошибка {error}')

    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all('article', class_='quote')
    # print(len(quotes))
    # # print(quotes)
    for citata in tqdm(quotes):
        citata_slovar = {}

        text = citata.find('p', class_='blockquote-text').get_text().strip()
        citata_slovar['Цитата'] = text
        istochnik = citata.find(
            'div', class_='readmore readmore-textual blockquote-origin')
        if istochnik is None:
            citata_slovar['Источник'] = None
        else:
            istochnik = istochnik.get_text().strip()
            citata_slovar['Источник'] = istochnik

        tema = citata.find('div', class_='blockquote-footnote')
        if tema is None:
            citata_slovar['Тема'] = None
        else:
            tema = tema.get_text(separator=', ', strip=True).strip()
            citata_slovar['Тема'] = tema

        # likes = citata.find('div', class_='action-bar').find('button', class_='muted action-bar-like')
        # print(likes)
        citata_slovar['Количество лайков'] = None
        data.append(citata_slovar)
        sleep(0.3)
    sleep(1)

massive_of_likes = []
with webdriver.Firefox() as driver: # лол меня блочит сайт с цитатми жирика я в ахуе
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument(f"user-agent={UserAgent().random}")
    driver = webdriver.Chrome(options=options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    for i in tqdm(range(1, 3)):
        url = f'https://ru.citaty.net/avtory/vladimir-volfovich-zhirinovskii/?page={i}'
        driver.get(url=url)
        driver.set_page_load_timeout(10)
        # driver.implicitly_wait(3)
        sleep(3)
        massive_of_buttons = driver.find_elements(By.CSS_SELECTOR, '.action-bar')
        for button_tags in massive_of_buttons:
            button = button_tags.find_element(By.CSS_SELECTOR, '.muted.action-bar-like')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_tags)
            button.click()
            sleep(0.1)
            likes = button_tags.find_element(By.CSS_SELECTOR, '.like-count')
            if likes.is_enabled() and likes.is_displayed():
                num_of_likes = float(likes.text.strip())
                massive_of_likes.append(num_of_likes)
        sleep(3)

print(massive_of_likes)

massive_of_likes = [410.0, 238.0, 177.0, 182.0, 167.0, 124.0, 100.0, 103.0, 47.0, 39.0, 44.0, 44.0, 86.0, 71.0, 48.0, 52.0, 50.0, 41.0, 118.0, 54.0, 50.0, 97.0, 77.0, 73.0, 72.0, 71.0, 71.0, 69.0, 69.0, 67.0, 64.0, 63.0, 60.0, 59.0, 55.0, 53.0, 51.0, 51.0, 51.0, 51.0, 47.0, 47.0, 46.0, 46.0, 46.0, 44.0, 44.0, 42.0, 40.0, 38.0, 37.0, 36.0, 36.0, 36.0, 34.0,
                    33.0, 33.0, 31.0, 28.0, 28.0, 27.0, 26.0, 25.0, 24.0, 24.0, 22.0, 21.0, 21.0, 21.0, 21.0, 19.0, 17.0, 16.0, 15.0, 14.0, 14.0, 13.0, 13.0, 13.0, 12.0, 12.0, 12.0, 11.0, 11.0, 11.0, 11.0, 11.0, 10.0, 10.0, 10.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 8.0, 8.0, 8.0, 7.0, 7.0, 7.0, 6.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0, 4.0, 4.0, 4.0, 3.0, 3.0, 3.0, 3.0]

for index in range(len(data)):
    data[index]['Количество лайков'] = massive_of_likes[index]

with open(r'D:\python_main\training_env\parsers_project\projects\zirinovskiy_citats\data\quotes.json', 'w', encoding='utf-8') as writer_file:
    json.dump(data, writer_file, ensure_ascii=False, indent=4)
end = time()
print(f'Парсер отработал за {round(end - start)} секунд')
