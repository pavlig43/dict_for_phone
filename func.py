import json

import requests
from googletrans import Translator


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


def tg_message(message):
    token = '6118490871:AAGTVlmAw3-a12tkEy8N9W6gXl2ofmD_8FU'
    chat_id = '5274223669'
    url = rf'https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}'
    requests.get(url)


def translate_word(word):
    translator = Translator()
    try:
        result = translator.translate(word, dest='ru')
        return result.text
    except:
        return word


def dictionary_txt():
    dictionary = {}
    with open('dictionary.txt', 'r', encoding='utf-8') as file:
        all_text = file.read().split('\n')[:10]
        for string in all_text:
            string = string.replace('"','').split(';')
            dictionary[string[0]] = {'translation': string[-1].split(","), 'pronunciations': string[-2] if
                                     len(string) == 3 else ''}
            # string = string.replace('"', '').rsplit(';',1)
            # term_transcription = string[0].replace(';', ' ')
            # term_transcription = string[0].split(';')[0]
            # values = string[1].split(',')
            # dictionary[term_transcription] = values

        return dictionary


if __name__ == '__main__':
    print(dictionary_txt())