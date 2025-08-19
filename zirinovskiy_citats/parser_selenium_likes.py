from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
from time import sleep
from fake_useragent import UserAgent
# from selenium.

# user_agent = UserAgent().random
# print(user_agent)

massive_of_likes = []
with webdriver.Chrome() as driver:
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
        # driver.set_page_load_timeout(3)
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