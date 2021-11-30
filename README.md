# Space photo loader

Easy way to download some beautiful pictures from SpaceX and NASA.

## How to prepare:
1. Make sure Python installed on your PC - you can get it from [official website](https://www.python.org/).
   

2. Install libraries with pip:
    ```
    pip3 install -r requirements.txt
    ```
3. Get your personal token for access to NASA API on [NASA website](https://api.nasa.gov/).
    Create .env file in directory with main.py file(use Notepad++) and add the string
    ```
    NASA_TOKEN='your_nasa_api_token'
    ```
    to it instead of value in quotes. Here and further quotes must be removed.
   

4. Create a Telegram bot which will post pictures to your own channel - just send message `/newbot` to [@BotFather](https://telegram.me/BotFather) and follow instructions.
    After bot will be created, get token from @BotFather and add to .env file:
    ```
    TELEGRAM_TOKEN='your_telegram_bot_token'
    ```
    Put your token instead of value in quotes.
   

5. Create your Telegram channel (or use existing) and make your bot admin in it. Add the string
    ```
    TELEGRAM_CHAT_ID=@'YourChannelID'
    ```
    to .env file. Instead of `YourChannelID` put your channel id (`@` symbol is required).
   

6. Add to .env file string:
    ```
    DELAY='time_of_delay_in_seconds'
    ``` 
    Instead of value in quotes indicate time when script should be started again in seconds.
    Default delay value is 24 hours.

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
usage: main.py [-h] [-c COUNT] [-dir DIRECTORY]

Загрузка фото космоса от SpaceX и NASA в Телеграм-канал

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        Кол-во фотографий NASA APOD
  -dir DIRECTORY, --directory DIRECTORY
                        Путь к папке для скачанных картинок
```
