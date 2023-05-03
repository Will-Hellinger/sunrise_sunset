import requests
import os
from bs4 import BeautifulSoup
import json

if os.name == 'nt':
    subdirectory = '\\'
    clear = 'cls'
else:
    subdirectory = '/'
    clear = 'clear'

months = ('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december')
month_abbreviations = ('jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
file_location = f'.{subdirectory}data{subdirectory}months{subdirectory}'


def save_file(file: bytes, data: dict):
    file.seek(0)
    json.dump(data, file, indent=4)
    file.truncate()


def abbreviate_month(month_name: str):
    global months
    global month_abbreviations

    return month_abbreviations[months.index(month_name)]


def get_month(month_index: int):
    global months

    return months[month_index- 1]


def scrape_data(years: list, city: str, location: str):
    city = city.lower()
    location = location.lower()

    urls = []

    for year in years:
        for month in range(1, 13):
            urls.append(f"https://www.timeanddate.com/sun/{location}/{city}?month={month}&year={year}")
    
    for url in urls:
        site = requests.get(url)
        site_soup = BeautifulSoup(site.content, 'html.parser')

        title = str(site_soup.findAll('h2')[1].text)
        table = site_soup.find('table', id='as-monthsun')
        days = table.findAll('tr', title='Click to expand for more details')

        month = str(title.split(' ')[0]).lower()
        year = int(title.split(' ')[1])

        filename = f'{abbreviate_month(month)}_{year}_{city}.json'

        with open(f'{file_location}{filename}', mode='w', encoding='utf-8') as file:
            file.write('{\n}')

        log_file = open(f'{file_location}{filename}', mode='r+', encoding='utf-8')
        data = json.load(log_file)

        for day in range(0, len(days)):
            row = days[day]

            sunrise = row.find('td', class_= 'c sep').text
            sunset = row.find('td', class_= 'sep c').text
            length = row.find('td', class_= 'c tr sep-l').text
            
            sunrise = sunrise.split(' ↑ ')[0]
            sunset = sunset.split(' ↑ ')[0]

            data[day + 1] = {'sunrise' : sunrise, 'sunset' : sunset, 'length' : length}

        save_file(log_file, data)
        log_file.close()