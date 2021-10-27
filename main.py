import requests
from dotenv import load_dotenv
import os
import urllib
import datetime


def get_image(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)


def get_spacex_links(launch_number):
    url = f'https://api.spacexdata.com/v3/launches/{launch_number}'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['links']['flickr_images']


def fetch_spacex_last_launch(folder, launch_number):
    spacex_folder = f'{folder}/spacex'
    os.makedirs(spacex_folder, exist_ok=True)
    filename = 'spacex'
    links = get_spacex_links(launch_number)
    for link_number, link in enumerate(links):
        path = f'{spacex_folder}/{filename}{link_number}.jpg'
        get_image(link, path)


def get_nasa_apod_links(count, api_key):
    url = 'https://api.nasa.gov/planetary/apod?'
    params = {'count': count,
              'api_key': api_key}
    response = requests.get(url, params=params)
    response.raise_for_status()
    nasa_links = []
    for image_data in response.json():
        nasa_links.append(image_data['url'])
    return nasa_links


def get_image_extension(url):
    parsed_url = urllib.parse.urlsplit(url, scheme='', allow_fragments=True)
    filepath = urllib.parse.unquote(parsed_url[2], encoding='utf-8', errors='replace')
    path, filename = os.path.split(filepath)
    name, extension = os.path.splitext(filename)
    return extension


def fetch_nasa_apod(folder, count, api_key):
    nasa_apod_folder = f'{folder}/nasa_apod'
    os.makedirs(nasa_apod_folder, exist_ok=True)
    filename = 'nasa_apod'
    links = get_nasa_apod_links(count, api_key)
    for link_number, link in enumerate(links):
        image_extension = get_image_extension(link)
        path = f'{nasa_apod_folder}/{filename}{link_number}{image_extension}'
        get_image(link, path)


def combine_nasa_epic_link(data, api_key):
    image_id, year, month, day = data
    url = 'https://api.nasa.gov/EPIC/archive/natural'
    url_template = f'{url}/{year}/{month}/{day}/png/{image_id}.png?api_key={api_key}'
    return url_template


def get_nasa_epic_links(api_key, days_ago):
    request_data = datetime.date.today() - datetime.timedelta(days=days_ago)
    url = f'https://epic.gsfc.nasa.gov/api/natural/date/{request_data}'
    response = requests.get(url)
    response.raise_for_status()
    links = []
    for image_data in response.json():
        date = datetime.datetime.fromisoformat(image_data['date'])
        link = combine_nasa_epic_link(
            (image_data['image'], date.year, date.month, date.day), api_key)
        links.append(link)
    return links


def fetch_nasa_epic(folder, days_ago, api_key):
    nasa_epic_folder = f'{folder}/nasa_epic'
    os.makedirs(nasa_epic_folder, exist_ok=True)
    filename = 'nasa_epic'
    links = get_nasa_epic_links(api_key, days_ago)
    for link_number, link in enumerate(links):
        path = f'{nasa_epic_folder}/{filename}{link_number}.png'
        get_image(link, path)


if __name__ == '__main__':
    load_dotenv()
    nasa_api_key = os.environ['NASA_TOKEN']
    image_folder = 'images'
    fetch_spacex_last_launch(image_folder, 16)
    fetch_nasa_apod(image_folder, 10, nasa_api_key)
    fetch_nasa_epic(image_folder, 8, nasa_api_key)
    print(f'Done! Check the "{image_folder}" folder for results!')
