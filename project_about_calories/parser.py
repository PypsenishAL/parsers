from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep
import requests
import csv
from tqdm import tqdm

main_url = 'https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie'
base_headers = {'user-agent': UserAgent().random}
csv_headers = ['Продукт', 'Калорийность', 'Белки', 'Жиры', 'Углеводы']
try:
    base_response = requests.get(url=main_url, headers=base_headers, timeout=(3, 3))
    base_response.raise_for_status()
    
except requests.exceptions.RequestException as error:
    print(f'Возникла ошибка на уровне запроса к сайту{error}')
    
    
base_soup = BeautifulSoup(base_response.text, 'html.parser')
massive_of_blocks_to_parse = base_soup.find_all('div', class_='uk-grid uk-grid-medium')

for block in tqdm(range(len(massive_of_blocks_to_parse))):
    print(f'\nНачали обрабатывать {block+1}-ый блок')
    massive_of_urls = [f'https://health-diet.ru' + str(elem.get('href')) for elem in massive_of_blocks_to_parse[block].find_all('a', href=True)]
    # print(massive_of_urls)
    
    with requests.Session() as session:
        session.headers.update(base_headers)
        for url in tqdm(massive_of_urls):
            try:
                response = session.get(url=url, timeout=(3, 3))
                response.raise_for_status()
            except requests.exceptions.RequestException as error:
                print(f'Возникла ошибка на уровне запроса по ссылке раздела продукто{error}')
                print(f'Ошибка в блоке обработки {block+1}')
                continue
                
            file_path = f'D:\\python_main\\training_env\\parsers_project\\projects\\project_about_calories\\data\\block_{block}.csv'
            with open(file_path, 'w', encoding='utf-8', newline='') as write_file:
                writer = csv.writer(write_file, delimiter=';')
                writer.writerow(csv_headers)
                    
                section_data_massive_to_write = []
                section_soup = BeautifulSoup(response.text, 'html.parser')
                body_rows = section_soup.find('tbody').find_all('tr')
                for row in body_rows:
                    title = row.find('td').get_text()
                    kkal, belki, ziri, yglevodi = [elem.get_text() for elem in row.find_all('td', class_= 'uk-text-right', limit=4)]
                    row_to_write = [title.strip(), float(kkal.split()[0].strip().replace(',', '.', count=1)), float(belki.split()[0].strip().replace(',', '.', count=1)), 
                                    float(ziri.split()[0].strip().replace(',', '.', count=1)), float(yglevodi.split()[0].strip().replace(',', '.', count=1))]
                    section_data_massive_to_write.append(row_to_write)
                        
                    writer.writerows(section_data_massive_to_write)
            sleep(0.3)
    print(f'Закончили обрабатывать {block+1}-ый блок\n')
    sleep(2)