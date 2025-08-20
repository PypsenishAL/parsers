from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from time import sleep
from time import time
import json
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm

start = time()
url = 'https://roscarservis.ru/catalog/legkovye/?arCatalogFilter_458_1500340406=Y&set_filter=Y&sort%5Brecommendations%5D=asc&limit=16'
data = []

options = Options()
options.add_argument(f"user-agent={UserAgent().random}")
# options.add_argument('--headless=new')
options.add_argument('--disable-ssl')
options.add_argument('--no-sandbox')
options.add_argument('--disable-extensions')
options.add_argument('--disable-web-security')
options.add_argument('--ignore-certificate-errors-spki-list')

with webdriver.Chrome(options=options) as browser:
    browser.set_page_load_timeout(2)
    try:
        browser.get(url=url)
        sleep(1.5)
    except TimeoutException:
        browser.execute_script('window.stop()')
        actions = ActionChains(browser)
        actions.send_keys(Keys.ESCAPE).perform()
        sleep(1)
    summer_tires_data = []
    
    wait = WebDriverWait(browser, 15)

    max_scrolls = 10
    current_scrolls = 0
    button_clicked = 0
    initially_body_height = browser.execute_script('return document.body.scrollHeight')
    print(f'Начали сбор всех шин')
    while current_scrolls < max_scrolls:
        for i in range(3):
            browser.execute_script('window.scrollBy(0, window.innerHeight * 0.8)')
            sleep(0.3)
            
        current_body_height = browser.execute_script('return document.body.scrollHeight')
        
        if initially_body_height == current_body_height:
            try:
                button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn--load-more')))
                sleep(0.3)
                browser.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                sleep(1)
                button.click()
                button_clicked += 1
                sleep(1)
                if button_clicked == 2:
                    print(f'Проскролли уже довольно сильно, остановимся пока на текущих результатах')
                    break
            except Exception as error:
                print(f'Домотали до конца, кнопки больше нет, {error}')
                break
        initially_body_height = current_body_height
        summer_tires = [str(elem.find_element(By.CSS_SELECTOR, 'a.product__image').get_attribute('href')) for elem in browser.find_elements(By.CSS_SELECTOR, '.product.animated, .product.cardAnimation_.animated') if elem not in summer_tires_data]
        if len(summer_tires) == 0:
            current_scrolls += 1
        else:
            current_scrolls = 0
            summer_tires_data.extend(summer_tires)
    # print(summer_tires_data)
    print(f'Закончили сбор всех шин, начинаем обработку каждой по отдельности')
    for tire_url in tqdm(summer_tires_data):
        tire_slovar = {}
        
        try:
            browser.get(url=tire_url)
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(1)
        except TimeoutException:
            # browser.execute_script('window.stop()')
            actions = ActionChains(browser)
            actions.send_keys(Keys.ESCAPE).perform()
            sleep(2)
        try:
            name = browser.find_element(By.XPATH, "//*[@id='roscar-app']/div[5]/section/div/div[2]/div[1]/div[2]/p").text.strip().split(maxsplit=2)[-1]
        except Exception as error:
            name = None
        tire_slovar['Название'] = name
        price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#roscar-app > div:nth-child(5) > section > div > div > div.product-screen__right > div.product-screen__bottom > div.product-screen__price > p.product-screen__price-value > span')))
        browser.execute_script('return arguments[0].scrollIntoView(true);', price)
        sleep(0.5)
        tire_slovar['Цена'] = price.text.strip().rsplit(maxsplit=1)
        screen_info = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-screen__info')))
        browser.execute_script('return arguments[0].scrollIntoView(true);', screen_info)
        for tag_li in screen_info.find_elements(By.TAG_NAME, 'li'):
            # massive_elements = wait.until()
            name, chiso = [elem.text.strip() for elem in tag_li.find_elements(By.TAG_NAME, 'span')]
            tire_slovar[name] = chiso
            
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        sleep(0.5)
        products_charki = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#product-characteristics > ul')))
        browser.execute_script('return arguments[0].scrollIntoView(true);', products_charki)
        # products_charki = browser.find_element(By.ID, 'product-characteristics').find_elements(By.TAG_NAME, 'li')
        for tag_li in products_charki.find_elements(By.TAG_NAME, 'li'):
            text, value = tag_li.find_element(By.TAG_NAME, 'p').text.strip(), tag_li.find_element(By.CSS_SELECTOR, '.product-desc__list-value').text.strip()
            tire_slovar[text] = value
        product_available = browser.find_element(By.ID, 'product-available').find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
        for tag_li in product_available:
            tire_slovar[tag_li.find_element(By.TAG_NAME, 'p').text.strip()] = tag_li.find_element(By.TAG_NAME, 'span').text.strip()
            
        data.append(tire_slovar)    
# print(data)
end = time()

with open(r'D:\python_main\training_env\parsers_project\projects\summer_tires\data\summer_tires.json', 'w', encoding='utf-8') as writer_file:
    json.dump(data, writer_file, indent=4, ensure_ascii=False)

print(f'Отработали за {round(end-start)} секунд. Собрали {len(summer_tires_data)} карточек.')