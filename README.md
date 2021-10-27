# Space photo loader

Easy way to download some beautiful pictures from SpaceX and NASA

## How to prepare:
1. Make shore Python installed on your PC - you can get it from [official website](https://www.python.org/)
2. Install libraries with pip:
`pip3 install -r requirements.txt`
3. Get your personal token for access to NASA API on [NASA website](https://api.nasa.gov/).
Create .env file in directory with main.py file(use Notepad++) and add the string `NASA_TOKEN='your_nasa_api_token'` to it (without any quotes).

## How to use:
Just run main.py in root directory. You'll see the message "Done! Check the "image_folder" for results!" when script will be finished.

## Available options
If you want to get different results, you can change settings in `"if __name__"` block:`
image_folder - this variable contains path to downloaded images;
fetch_spacex_last_launch() - 2nd argument in this function is number of SpaseX launch;
fetch_nasa_apod() - 2nd argument in this function is number of random space pictures;
fetch_nasa_epic() - 2nd argument in this function indicates how many days ago photos of the Earth were taken.