import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep
from time import time
from tqdm import tqdm
import json

start = time()

headers = {'user-agent': UserAgent().random}
longest_dict = {}
len_longest_dict = 0
massive = []

base_url = 'http://duma.gov.ru/duma/deputies/'
try:
    base_response = requests.get(base_url, timeout=(3,3))
    base_response.raise_for_status()
    base_response.encoding = 'utf-8'
    print(base_response.status_code, base_response.reason)
    if base_response.ok:
        pass
    else:
        raise requests.exceptions.RequestException
except requests.exceptions.RequestException as error:
    print(f'Ошибка на уровне самого первичного запроса к сайту госдумы {error}')
    
base_soup = BeautifulSoup(base_response.text, 'html.parser')
alphabet_spisok_persons = base_soup.find_all('ul', class_='list-persons list-persons--deputy grid grid--three-columns mobile-no-padding')
alphabet_spisok = base_soup.find_all('h2', class_='section__title section__title--l')


for bukva, list_persons in tqdm(zip(alphabet_spisok, alphabet_spisok_persons), total=len(alphabet_spisok_persons)):
    print(f'\nНачали обработку фамилий, начинающихся на {bukva.get_text().strip()}')
    list_bukva_persons_urls = [f'http://duma.gov.ru' + str(elem.find('a', attrs={'itemprop': 'url'}).get('href'))
                               for elem in list_persons.find_all('li', class_='list-persons__item')]
    for person_url in (list_bukva_persons_urls):
        person_headers = {'user-agent': UserAgent().random}
        with requests.Session() as session:
            session.headers.update(person_headers)
            try:    
                person_response = requests.get(person_url, timeout=(3, 3))
                base_response.raise_for_status()
                if base_response.ok:
                    pass
                else:
                    raise requests.exceptions.RequestException
            except requests.exceptions.RequestException as error:
                print(f'Ошибка на уровне запроса к депутату Госдумы, {error}')
            person_soup = BeautifulSoup(person_response.text, 'html.parser')
            person_info = person_soup.find_all('section', class_='section section--page section--mobile')
            
            person_slovar = {}
            
            fraction_region_info = person_soup.find('div', class_='person__description__grid').find_all('div')
            person_slovar['Фракция'] = fraction_region_info[1].get_text().strip()
            person_slovar['Регион'] = fraction_region_info[-1].get_text().strip()
            try:
                _fio = person_soup.find('h1', class_='article__title article__title--person').get_text(separator=' ',strip=True).strip()
                person_slovar['ФИО'] = _fio
            except Exception as er:
                print(f'Ошибка {er}, обрабатывали {person_url}')
                continue
            
            for data in person_info:
                info_name = data.find('h2', class_='section__title section__title--page').get_text().strip()
                if info_name == 'Информация о депутате':
                    birthday, vstyplenie = [elem.get_text().strip().split(': ') for elem in data.find_all('p')]
                    person_slovar['Дата рождения'] = birthday
                    person_slovar['Дата вступления в полномочия'] = vstyplenie
                elif info_name == 'Сведения об избрании':
                    date = data.find('dt').get_text().strip()
                    izran = data.find('p').get_text().strip()
                    person_slovar['Дата избрания'] = date
                    person_slovar['Партия'] = izran
                elif info_name == 'Комитеты и комиссии':
                    spisok_komisiy = [elem.get_text().strip() for elem in data.find_all('dd')]
                    person_slovar['Комитеты и комиссии'] = spisok_komisiy
                elif info_name == 'Образование':
                    education = [elem.get_text().strip() for elem in data.find_all('dd')]
                    date_education = [elem.get_text().strip() for elem in data.find_all('dt')]
                    person_slovar['Образование'] = education[-1]
                    person_slovar['Окончание образования'] = date_education[-1]
                elif info_name == 'Ученые степени':
                    educat_stepen = data.find('div', class_='text text--m').get_text().strip()
                    person_slovar['Ученые степени'] = educat_stepen
            # if len/(person_slovar) > len_longest_dict:
                # 
            massive.append(person_slovar)
        sleep(0.3)
    sleep(1)
    print(f'Закончили обработку фамилий, начинающихся на {bukva.get_text().strip()}\n')
    
print(massive)

with open(r'D:\python_main\training_env\parsers_project\projects\duma_gov_deputats\data\duma.json', 'w', encoding='utf-8') as writer_file:
    json.dump(massive, writer_file, ensure_ascii=False, indent=4)

end = time()
print(f'Отработали за {round(end - start)} секунд.')