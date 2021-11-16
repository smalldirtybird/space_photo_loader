import requests
from dotenv import load_dotenv
import os
import urllib
import datetime
import argparse
import telegram
import time
import shutil
import random


def write_string_into_log(message):
    with open('log.txt', 'a') as logfile:
        time_stamp = datetime.datetime.now()
        logfile.write(f'{time_stamp}. {message}\n')


def get_exception(location, exception):
    message = f'Exception of type {type(exception).__name__} occurred in {location}: {exception}'
    with open('log.txt', 'a') as logfile:
        time_stamp = datetime.datetime.now()
        logfile.write(f'{time_stamp}. {message}\n')
    print(message)


def get_image(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


def get_random_flight_number():
    flight_numbers = []
    url = 'https://api.spacexdata.com/v3/launches'
    response = requests.get(url)
    for flight in response.json():
        flight_numbers.append(flight['flight_number'])
    random_flight_number = random.choice(flight_numbers)
    return random_flight_number


def get_spacex_links(launch_number):
    url = f'https://api.spacexdata.com/v3/launches/{launch_number}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['links']['flickr_images']


def check_image_quantity(folder, folder_number):
    sub_folder = f'{folder}/{folder_number}'
    os.makedirs(sub_folder, exist_ok=True)
    if len(os.listdir(sub_folder)) == 9:
        folder_number += 1
    return sub_folder, folder_number


def fetch_spacex_last_launch(settings, token):
    spacex_folder = f"{settings['directory']}/spacex"
    filename = 'spacex'
    flight_number = get_random_flight_number()
    links = []
    while len(links) == 0:
        links = get_spacex_links(flight_number)
    write_string_into_log(f'received {len(links)} spacex links')
    folder_number = 0
    num_of_link = 0
    for link_number, link in enumerate(links):
        sub_folder, folder_number = check_image_quantity(
            spacex_folder, folder_number)
        path = f'{sub_folder}/{filename}{link_number}.jpg'
        get_image(link, path)
        num_of_link += 1
    write_string_into_log(f'{num_of_link} images has downloaded')
    post_to_telegram_channel(
        token, settings['telegram_chat_id'], spacex_folder)


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


def fetch_nasa_apod(settings, api_key, token):
    nasa_apod_folder = f"{settings['directory']}/nasa_apod"
    filename = 'nasa_apod'
    links = get_nasa_apod_links(settings['image_quantity'], api_key)
    write_string_into_log(f'received {len(links)} apod links')
    folder_number = 0
    num_of_link = 0
    for link_number, link in enumerate(links):
        sub_folder, folder_number = check_image_quantity(
            nasa_apod_folder, folder_number)
        image_extension = get_image_extension(link)
        if image_extension != '':
            path = f'{sub_folder}/{filename}{link_number}{image_extension}'
            get_image(link, path)
            num_of_link += 1
    write_string_into_log(f'{num_of_link} images has downloaded')
    post_to_telegram_channel(
        token, settings['telegram_chat_id'], nasa_apod_folder)


def combine_nasa_epic_link(data, api_key):
    image_id, year, month, day = data
    url = 'https://api.nasa.gov/EPIC/archive/natural'
    url_template = f'{url}/{year}/{month}/{day}' \
        f'/png/{image_id}.png?api_key={api_key}'
    return url_template


def get_nasa_epic_links(api_key, days_ago):
    request_data = datetime.date.today() - datetime.timedelta(days=int(days_ago))
    url = f'https://epic.gsfc.nasa.gov/api/natural/date/{request_data}'
    response = requests.get(url)
    response.raise_for_status()
    links = []
    for image_data in response.json():
        date, time = str(datetime.datetime.fromisoformat(image_data['date'])).split(sep=' ')
        year, month, day = date.split(sep='-')
        link = combine_nasa_epic_link(
            (image_data['image'], year, month, day), api_key)
        links.append(link)
    return links


def fetch_nasa_epic(settings, api_key, token):
    nasa_epic_folder = f"{settings['directory']}/nasa_epic"
    filename = 'nasa_epic'
    links = get_nasa_epic_links(api_key, settings['days_ago'])
    write_string_into_log(f'received {len(links)} epic links')
    folder_number = 0
    num_of_link = 0
    for link_number, link in enumerate(links):
        sub_folder, folder_number = check_image_quantity(
            nasa_epic_folder, folder_number)
        path = f'{sub_folder}/{filename}{link_number}.png'
        get_image(link, path)
        num_of_link += 1
    write_string_into_log(f'{num_of_link} images has downloaded')
    post_to_telegram_channel(
        token, settings['telegram_chat_id'], nasa_epic_folder)


def post_to_telegram_channel(token, chat_id, folder):
    bot = telegram.Bot(token=token)
    for sub_folder in os.listdir(folder):
        sub_folder_paths = f'{folder}/{sub_folder}'
        sub_folder_content = os.listdir(sub_folder_paths)
        media_group = []
        for image in sub_folder_content:
            image_path = f'{sub_folder_paths}/{image}'
            media = telegram.files.inputmedia.InputMediaPhoto(
                media=open(image_path, 'rb'))
            media_group.append(media)
        bot.send_media_group(chat_id=chat_id, media=media_group)
        write_string_into_log(f'{folder}/{sub_folder} successfully uploaded')
        time.sleep(60)


def get_arguments():
    parser = argparse.ArgumentParser(
        description='Загрузка фото космоса от SpaceX и NASA в Телеграм-канал')
    parser.add_argument(
        '-l', '--launch_number',
        help='Номер запуска SpaseX')
    parser.add_argument(
        '-c', '--count', default=9,
        help='Кол-во фотографий NASA APOD')
    parser.add_argument(
        '-d', '--days_ago', default=8,
        help='Как давно сделаны фото NASA EPIC')
    parser.add_argument(
        '-dir', '--directory', default='images',
        help='Путь к папке для скачанных картинок')
    args = parser.parse_args()
    args_dict = {'directory': args.directory,
                 'launch_number': args.launch_number,
                 'image_quantity': args.count,
                 'days_ago': args.days_ago
                 }
    return args_dict


def wait_before_nex_post(time_in_seconds=10):
    time.sleep(time_in_seconds)
    print(f'finish, next start in {time_in_seconds} seconds')


if __name__ == '__main__':
    arguments = get_arguments()
    load_dotenv()
    nasa_api_key = os.environ['NASA_TOKEN']
    telegram_token = os.environ['TELEGRAM_TOKEN']
    arguments['telegram_chat_id'] = os.environ['TELEGRAM_CHAT_ID']
    delay = int(os.environ['DELAY'])
    count = 1
    while True:
        print(f'Sending image pack #{count} at {datetime.datetime.now()}')
        try:
            fetch_spacex_last_launch(arguments, telegram_token)
        except Exception as e:
            get_exception('Spacex part', e)
        try:
            fetch_nasa_apod(arguments, nasa_api_key, telegram_token)
        except Exception as e:
            get_exception('Apod part', e)
        try:
            fetch_nasa_epic(arguments, nasa_api_key, telegram_token)
        except Exception as e:
            get_exception('Epic part', e)
        shutil.rmtree(arguments['directory'])
        wait_before_nex_post(delay)
        count += 1
