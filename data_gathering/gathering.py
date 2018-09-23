
import logging

import sys


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def gather_process():
    logger.info("gather")

    import requests
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    from lxml import html
    import csv
    import re

    # функция записи в файл списков данных построчно
    def csv_writer(data, path):
        # записываем данные в файл
        with open(path, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in data:
                writer.writerow(line)

    # establishing session
    s = requests.Session()

    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    })

    # определение ссылки на пользовательский список - рейтинг фильмов imdb
    url = 'https://www.imdb.com/user/ur19693291/ratings?ref_=nv_usr_rt_4'
    # запрос по ссылке
    res = requests.get(url)

    IMDB_data = []
    IMDB_data.append(['Name', 'Year', 'Genres', 'IMDBRate', 'MyRate', 'Voters'])
    # парсинг страниц с рейтингом, создание списков для записи в файл
    while True:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml")
        filmS = soup.findAll('div', {'class': 'lister-item-content'})
        for film in filmS:
            titleref = film.find('h3', {'class': 'lister-item-header'})
            moviename = str(titleref.find('a').text.strip())
            # link = titleref.find('a').get('href')
            yeartxt = film.find('span', {'class': "lister-item-year text-muted unbold"}).text
            # оставляем только цифры в строке с годом выпуска
            yearfull = ''.join(re.findall(r'\d', yeartxt))
            year = yearfull[0:4]

            genresIF = film.find('span', {'class': "genre"})
            if genresIF:
                genres = genresIF.text.strip().replace(',', '')
            else:
                genres = 'Undefined'

            IMDBratings = film.find('div', {'class': 'ipl-rating-star small'})
            IMDBrating = IMDBratings.find('span', {'class': "ipl-rating-star__rating"}).text.replace(',', '.')

            Myratings = film.find('div', {'class': 'ipl-rating-star ipl-rating-star--other-user small'})
            Myrating = Myratings.find('span', {'class': "ipl-rating-star__rating"}).text.replace(',', '.')

            Voters = film.find('span', {'name': 'nv'}).text.replace(',', '')

            IMDB_data.append([moviename, year, genres, IMDBrating, Myrating, Voters])

        page = soup.find('div', {'class': 'list-pagination'})
        endornot = page.find('span').text

        range1 = endornot.find('-')
        range2 = endornot.find('of')
        str3 = endornot[(range1 + 1):(range2)].strip()
        str4 = endornot[(range2 + 2):].strip()

        if str3 == str4:
            break
        else:
            movie_link = page.find('a', {'class': 'flat-button lister-page-next next-page'}).get('href')
            url = urljoin('https://www.imdb.com', movie_link)

    data = IMDB_data
    path = "output.csv"
    csv_writer(data, path)

def stats_of_data():
    logger.info("stats")



if __name__ == '__main__':

    logger.info("Work started")


    if sys.argv[1] == 'gather':
        gather_process()
        # print('HW1')

        print("check your list")

    elif sys.argv[1] == 'transform':
        convert_data_to_table_format()
        # print('HW2')
    elif sys.argv[1] == 'stats':
        # print('HW3')
        import pandas as pd
        import numpy as np

        datas = pd.read_csv("output.csv", sep=';', header=0)

        print('Мой средний рейтинг -', datas.MyRate.mean(), 'Средний рейтинг IMDB -', datas.IMDBRate.mean())
        print('----------------')
        print('Минимальное число проголосовавших -', datas.Voters.min(), 'за',
          str(datas[datas.Voters == datas.Voters.min()]['Name']))
        print('----------------')
        print('Максимальное число проголосовавших', datas.Voters.max(), 'за ',
          str(datas[datas.Voters == datas.Voters.max()]['Name']))
        print('----------------')
        print('Годы в выборке с ', datas.Year.min(), 'по ', datas.Year.max())
        print('----------------')
        Year_groupby = datas.groupby('Year');

        meanbyYear = datas.groupby('Year').mean()

        databymean = Year_groupby.aggregate(np.mean)

        RatesMean = databymean.iloc[:, 0:2]

        print("статистика c группировкой по году выпуска")

        print(RatesMean.describe())

        logger.info("work ended")
