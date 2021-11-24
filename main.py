import requests
from dotenv import load_dotenv
import os
import urllib
import datetime
import argparse
import telegram
import time
import shutil
from PIL import Image
import logging


def get_file_size(filepath):
    size_in_bytes = os.path.getsize(filepath)
    size_in_megabytes = size_in_bytes / (1024 ** 2)
    return size_in_megabytes


def big_file_compression(filepath, original_file_size, max_size):
    coefficient = max_size / original_file_size
    original_image = Image.open(filepath)
    original_width, original_height = original_image.size
    requirement_resolution = (
        round(original_width * coefficient),
        round(original_height * coefficient)
        )
    requirement_image = original_image.resize(
        requirement_resolution, Image.ANTIALIAS)
    requirement_image.save(filepath, optimize=True, quality=95)


def get_image(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)
    original_file_size = get_file_size(path)
    max_file_size = 20
    if original_file_size > max_file_size:
        big_file_compression(path, original_file_size, max_file_size)


def get_latest_flight_number():
    url = 'https://api.spacexdata.com/v3/launches'
    response = requests.get(url)
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


def check_image_quantity(folder, folder_number):
    sub_folder = os.path.join(folder, str(folder_number))
    os.makedirs(sub_folder, exist_ok=True)
    if len(os.listdir(sub_folder)) == 9:
        folder_number += 1
    return sub_folder, folder_number


def fetch_spacex_last_launch(folder, chat_id, token):
    spacex_folder = os.path.join(folder, 'spacex')
    filename = 'spacex'
    links = get_spacex_links(get_latest_flight_number())
    logging.info(f'received {len(links)} spacex links')
    folder_number = 0
    for link_number, link in enumerate(links):
        sub_folder, folder_number = check_image_quantity(
            spacex_folder, folder_number)
        path = os.path.join(sub_folder, f'{filename}{link_number}.jpg')
        get_image(link, path)
    post_to_telegram_channel(
        token, chat_id, spacex_folder)


def get_nasa_apod_links(count_apod, api_key):
    url = 'https://api.nasa.gov/planetary/apod?'
    params = {'count': count_apod,
              'api_key': api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    nasa_links = []
    for image_data in response.json():
        if image_data['media_type'] == 'image':
            nasa_links.append(image_data['url'])
    return nasa_links


def get_image_extension(url):
    parsed_url = urllib.parse.urlsplit(url, scheme='', allow_fragments=True)
    filepath = urllib.parse.unquote(parsed_url[2],
                                    encoding='utf-8', errors='replace')
    path, filename = os.path.split(filepath)
    name, extension = os.path.splitext(filename)
    return extension


def fetch_nasa_apod(folder, image_quantity, chat_id, api_key, token):
    nasa_apod_folder = os.path.join(folder, 'nasa_apod')
    filename = 'nasa_apod'
    links = get_nasa_apod_links(image_quantity, api_key)
    logging.info(f'received {len(links)} apod links')
    folder_number = 0
    for link_number, link in enumerate(links):
        sub_folder, folder_number = check_image_quantity(
            nasa_apod_folder, folder_number)
        image_extension = get_image_extension(link)
        if image_extension != '':
            path = os.path.join(sub_folder,
                                f'{filename}{link_number}{image_extension}')
            get_image(link, path)
    post_to_telegram_channel(
        token, chat_id, nasa_apod_folder)


def combine_nasa_epic_link(data, api_key):
    image_id, year, month, day = data
    url = 'https://api.nasa.gov/EPIC/archive/natural'
    url_template = f'{url}/{year}/{month}/{day}' \
        f'/png/{image_id}.png?api_key={api_key}'
    return url_template


def get_nasa_epic_links(api_key):
    days_ago = 0
    response_elements = []
    while len(response_elements) == 0:
        request_data = datetime.date.today() - datetime.timedelta(
            days=int(days_ago))
        url = f'https://epic.gsfc.nasa.gov/api/natural/date/{request_data}'
        response = requests.get(url)
        response.raise_for_status()
        response_elements = [
            elm for elm in response.json() if len(response.json()) != 0]
        days_ago += 1
    links = []
    for image_data in response.json():
        image_date, image_time = str(
            datetime.datetime.fromisoformat(image_data['date'])).split(sep=' ')
        year, month, day = image_date.split(sep='-')
        link = combine_nasa_epic_link(
            (image_data['image'], year, month, day), api_key)
        links.append(link)
    return links


def fetch_nasa_epic(folder, chat_id, api_key, token):
    nasa_epic_folder = os.path.join(folder, 'nasa_epic')
    filename = 'nasa_epic'
    links = get_nasa_epic_links(api_key)
    logging.info(f'received {len(links)} epic links')
    folder_number = 0
    for link_number, link in enumerate(links):
        sub_folder, folder_number = check_image_quantity(
            nasa_epic_folder, folder_number)
        path = os.path.join(sub_folder, f'{filename}{link_number}.png')
        get_image(link, path)
    post_to_telegram_channel(
        token, chat_id, nasa_epic_folder)


def post_to_telegram_channel(token, chat_id, folder):
    bot = telegram.Bot(token=token)
    for sub_folder in os.listdir(folder):
        sub_folder_paths = os.path.join(folder, sub_folder)
        sub_folder_content = os.listdir(sub_folder_paths)
        media_group = []
        for image in sub_folder_content:
            image_path = os.path.join(sub_folder_paths, image)
            media = telegram.files.inputmedia.InputMediaPhoto(
                media=open(image_path, 'rb'))
            media_group.append(media)
        bot.send_media_group(chat_id=chat_id, media=media_group)
        logging.info(f'{sub_folder_paths} successfully uploaded')
        time.sleep(60)


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
    args_dict = {'directory': args.directory,
                 'image_quantity': args.count
                 }
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
        try:
            fetch_spacex_last_launch(image_folder, telegram_chat_id, telegram_token)
        except Exception:
            logging.exception('fetch_spacex_last_launch')
        try:
            fetch_nasa_apod(image_folder, apod_photo_count, telegram_chat_id, nasa_api_key, telegram_token)
        except Exception:
            logging.exception('fetch_nasa_apod')
        try:
            fetch_nasa_epic(image_folder, telegram_chat_id, nasa_api_key, telegram_token)
        except Exception:
            logging.exception('fetch_nasa_epic')
        try:
            shutil.rmtree(image_folder)
        except Exception:
            logging.exception('shutil.rmtree')
        try:
            time.sleep(int(os.environ['DELAY']))
        except KeyError:
            logging.exception(f'''
                Variable "DELAY" not found in .env file.
                Default time of delay between script running is 24 hours.
                If need to set another delay value,
                check README.md for instructions.
                ''')
            time.sleep(86200)
