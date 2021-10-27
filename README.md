# Space photo loader

Easy way to download some beautiful pictures from SpaceX and NASA

## How to prepare:
1. Make shore Python installed on your PC - you can get it from [official website](https://www.python.org/)
2. Install libraries with pip:
`pip3 install -r requirements.txt`
3. Get your personal token for access to NASA API on [NASA website](https://api.nasa.gov/).
Create .env file in directory with main.py file(use Notepad++) and add the string `NASA_TOKEN='your_nasa_api_token'` to it (without any quotes).

## How to use:
Run `main.py` with console. Use `cd` command if you need to change directory:
```
D:\>cd D:\learning\python\api_services\space_photo_loader
D:\learning\python\api_services\space_photo_loader>python main.py
```
## Available options
If you want to get different results, you can use optional arguments in console with running main.py.
Get available options with `-h` argument:
```
D:\learning\python\api_services\space_photo_loader>python main.py -h
usage: main.py [-h] [-l LAUNCH_NUMBER] [-c COUNT] [-d DAYS_AGO] [-dir DIRECTORY]

Загрузите красивые фото космоса от SpaceX и NASA

optional arguments:
  -h, --help            show this help message and exit
  -l LAUNCH_NUMBER, --launch_number LAUNCH_NUMBER
                        Номер запуска SpaseX
  -c COUNT, --count COUNT
                        Кол-во фотографий NASA APOD
  -d DAYS_AGO, --days_ago DAYS_AGO
                        Как давно сделаны фото NASA EPIC
  -dir DIRECTORY, --directory DIRECTORY
                        Путь к папке для скачанных картинок
```