import requests
from dotenv import load_dotenv
import os
import urllib
import datetime
import argparse
import telegram
import time
import shutil
import logging
import random


def get_file_size(filepath):
    size_in_bytes = os.path.getsize(filepath)
    size_in_megabytes = size_in_bytes / (1024 ** 2)
    return size_in_megabytes


def download_image(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


def get_number_of_latest_flight_with_images():
    url = 'https://api.spacexdata.com/v3/launches'
    response = requests.get(url)
    response.raise_for_status()
    flights = response.json()
    flights.reverse()
    for flight in flights:
        if len(flight['links']['flickr_images']):
            break
    return flight['flight_number']


def get_spacex_links(launch_number):
    url = f'https://api.spacexdata.com/v3/launches/{launch_number}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['links']['flickr_images']


def fetch_spacex_last_launch(folder):
    filename = 'spacex'
    links = get_spacex_links(get_number_of_latest_flight_with_images())
    for link_number, link in enumerate(links):
        path = os.path.join(folder, f'{filename}{link_number}.jpg')
        download_image(link, path)


def get_nasa_apod_links(count, api_key):
    url = 'https://api.nasa.gov/planetary/apod?'
    params = {'count': count,
              'api_key': api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    nasa_links = []
    for image in response.json():
        if image['media_type'] == 'image':
            nasa_links.append(image['url'])
    return nasa_links


def get_image_extension(url):
    parsed_url = urllib.parse.urlsplit(url, scheme='', allow_fragments=True)
    filepath = urllib.parse.unquote(parsed_url[2],
                                    encoding='utf-8', errors='replace')
    path, filename = os.path.split(filepath)
    name, extension = os.path.splitext(filename)
    return extension


def fetch_nasa_apod(folder, image_quantity, api_key):
    filename = 'nasa_apod'
    links = get_nasa_apod_links(image_quantity, api_key)
    for link_number, link in enumerate(links):
        image_extension = get_image_extension(link)
        if image_extension:
            path = os.path.join(folder,
                                f'{filename}{link_number}{image_extension}')
            download_image(link, path)


def combine_nasa_epic_link(image_id, year, month, day, api_key):
    url = 'https://api.nasa.gov/EPIC/archive/natural'
    url_template = f'{url}/{year}/{month}/{day}' \
        f'/png/{image_id}.png?api_key={api_key}'
    return url_template


def get_nasa_epic_links(api_key):
    days_ago = 0
    response_elements = []
    while not len(response_elements):
        date_for_url = datetime.date.today() - datetime.timedelta(
            days=int(days_ago))
        url = f'https://epic.gsfc.nasa.gov/api/natural/date/{date_for_url}'
        response = requests.get(url)
        response.raise_for_status()
        response_elements = [
            elm for elm in response.json() if len(response.json())]
        days_ago += 1
    links = []
    for image in response.json():
        image_date, image_time = str(
            datetime.datetime.fromisoformat(image['date'])).split(sep=' ')
        year, month, day = image_date.split(sep='-')
        link = combine_nasa_epic_link(
            image['image'], year, month, day, api_key)
        links.append(link)
    return links


def fetch_nasa_epic(folder, api_key):
    filename = 'nasa_epic'
    links = get_nasa_epic_links(api_key)
    for link_number, link in enumerate(links):
        path = os.path.join(folder, f'{filename}{link_number}.png')
        download_image(link, path)


def post_to_telegram_channel(token, chat_id, folder, delay=86400):
    bot = telegram.Bot(token=token)
    images = os.listdir(folder)
    random.shuffle(images)
    photo_size_limit = 20
    for image in images:
        filepath = os.path.join(folder, image)
        file_size = get_file_size(filepath)
        with open(filepath, 'rb') as file:
            if file_size < photo_size_limit:
                bot.send_photo(chat_id=chat_id, photo=file)
            else:
                bot.send_document(chat_id=chat_id, document=file)
        time.sleep(delay)


def get_arguments():
    parser = argparse.ArgumentParser(
        description='Загрузка фото космоса от SpaceX и NASA в Телеграм-канал')
    parser.add_argument(
        '-c', '--count', default=10,
        help='Кол-во фотографий NASA APOD')
    parser.add_argument(
        '-dir', '--directory', default='images',
        help='Путь к папке для скачанных картинок')
    args = parser.parse_args()
    return args.directory, args.count


if __name__ == '__main__':
    logging.basicConfig(
        filename='logs.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s')
    image_folder, apod_photo_count = get_arguments()
    load_dotenv()
    nasa_api_key = os.environ['NASA_TOKEN']
    telegram_token = os.environ['TELEGRAM_TOKEN']
    telegram_chat_id = os.environ['TELEGRAM_CHAT_ID']
    while True:
        os.makedirs(image_folder, exist_ok=True)
        try:
            fetch_spacex_last_launch(image_folder)
            fetch_nasa_apod(image_folder, apod_photo_count, nasa_api_key)
            fetch_nasa_epic(image_folder, nasa_api_key)
        except Exception as e:
            logging.exception(e)
        post_to_telegram_channel(telegram_token,
                                 telegram_chat_id,
                                 image_folder,
                                 int(os.environ['DELAY'])
                                 )
        shutil.rmtree(image_folder)
