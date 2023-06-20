import json

import requests


def get_list_value(file_name):
    try:
        with open(file_name, 'r') as file:
            try:
                value = json.load(file)
            except json.decoder.JSONDecodeError:
                value = {}
    except FileNotFoundError:
        with open(file_name, 'w') as file:
            value = {}
    return value


token = '6118490871:AAGTVlmAw3-a12tkEy8N9W6gXl2ofmD_8FU'
chat_id = '5274223669'


def tg_message(message):
    url = rf'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    requests.get(url)


if __name__ == '__main__':
    tg_message('Hello')
