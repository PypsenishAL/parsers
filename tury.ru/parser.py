import requests
from bs4 import BeautifulSoup
from time import sleep
from time import time
import json
from fake_useragent import UserAgent
from tqdm import tqdm

start = time()
headers = {'user-agent': UserAgent().random}
base_url = 'https://tury.ru/hotel/'
was_written = []
_data = []
count = 0 
unique_count = 0
try:
    base_response = requests.get(url=base_url, headers=headers, timeout=(3, 3))
    base_response.raise_for_status()
    
except requests.exceptions.RequestException as error:
    print(f'Ошибка на уровне первичного запроса к странице {error}')
    
base_soup = BeautifulSoup(base_response.text, 'html.parser')
pagen_tuple = [(f'https://tury.ru' + str(elem.get('href')), str(elem.find('div').get_text())) for elem in base_soup.find('div', class_='pop_hotels').find_all('a', href=True)] 
 
for type_url, type_name in tqdm(pagen_tuple):
    print(f'\nНачали обработку отелей по типу отдыха: {type_name}')
    type_headers = {'user-agent': UserAgent().random}
    with requests.Session() as session:
        session.headers.update(type_headers)
        try:
            type_response = session.get(url=type_url, timeout=(3, 3))
            type_response.raise_for_status()
            if not type_response.ok:
                raise requests.exceptions.RequestException('Запрос к странице-категории с отелями вернул не 200 код')
            print(f'Успешный запрос к странице-категории отелей по ссылке {type_url}\n')
            
        except requests.exceptions.RequestException as error:
            print(f'Ошибка на уровне запроса к странице отелей с категорией {type_name}')
            print(error)
            
        type_soup = BeautifulSoup(type_response.text, 'html.parser')
        # print(type_soup.find('div', class_='page').find('div', class_='container').find('div', class_='reviews-travel__content flex'))
        # break
        massive_of_hotels = [(elem.find('a', href=True).get('href'), elem.find('a').find('div').get_text()) for elem in type_soup.find('div', class_='reviews-travel__column').find_all('div', class_='reviews-travel__info')]
        
        for hotel_url, hotel_name in tqdm(massive_of_hotels):
            count += 1
            if hotel_name in was_written:
                continue
            else:
                unique_count += 1
                was_written.append(hotel_name)
                try:
                    hotel_page_response = session.get(hotel_url, timeout=(3, 3))
                    hotel_page_response.raise_for_status()
                    
                except requests.exceptions.RequestException as error:
                    print(f'Ошибка на уровне запроса к странице самого отеля с по ссылке {hotel_url}')
                    print(error)
                     
                hotel_page_soup = BeautifulSoup(hotel_page_response.text, 'html.parser')
                main_hotel_name = hotel_page_soup.find('div', class_='h1').get_text().strip()
                location = hotel_page_soup.find('div', class_='showplace__wrapp').find('div', class_='showplace__text').get_text().strip()
                
                meal_section = hotel_page_soup.find('section', id='meal')
                meal_slovar = {}
                if meal_section is not None:
                    meal_section = meal_section.find('div', class_='about-hotel__item')
                    if meal_section is not None:
                        meal_section = meal_section.find_all('ul')
                        for tag in meal_section:
                            name_razdela, *data_meal = [elem.get_text().strip() for elem in tag.find_all('li')]
                            meal_slovar[name_razdela] = data_meal
                        else:
                            meal_slovar = None
                else:
                    meal_slovar = None
                
                service_section = hotel_page_soup.find('section', id='service')
                service_slovar = {}
                if service_section is not None:
                    service_section = service_section.find('div', class_='about-hotel__item')
                    if service_section is not None:
                        service_section = service_section.find_all('ul')
                        for tag in service_section:
                            name_razdela, *data_Service = [elem.get_text().strip() for elem in tag.find_all('li')]
                            service_slovar[name_razdela] = data_Service
                        else:
                            service_slovar = None
                else:
                    service_slovar = None
                    
                funsport_sections = hotel_page_soup.find_all('section', id='funsport')
                funsport_slovar = {}
                if len(funsport_sections) != 0:
                    for funsport_section in funsport_sections:
                        name_funsport_section = funsport_section.find('div', class_='h2').get_text().strip()
                        funsport_data = funsport_section.find('div', class_='about-hotel__item').find_all('ul')
                        section_slovar = {}
                        for tag in funsport_data:
                            name_razdela, *data_fun = [elem.get_text().strip() for elem in tag.find_all('li')]
                            section_slovar[name_razdela] = data_fun
                            
                        funsport_slovar[name_funsport_section] = section_slovar
                else:
                    funsport_slovar = None
                    
                dict_to_write = {'Название': main_hotel_name, 'Расположение': location,
                                    'Питание': meal_slovar, 'Сервис': service_slovar, 'Отдых и концепция': funsport_slovar}
                _data.append(dict_to_write)
                
            sleep(0.3)   
    print(f'Закончили обработку отелей по типу отдыха: {type_name}\n')
    sleep(2)
print(_data)
end = time()
with open(r'D:\python_main\training_env\parsers_project\projects\tury.ru\data\file.json', 'w', encoding='utf-8') as write_file:
    writer = json.dump(_data, write_file, ensure_ascii=False, indent=4)   

print(f'Отработал за {round(end - start)} секунд. Всего {count} отелей, из которых было записано {unique_count} уникальных')