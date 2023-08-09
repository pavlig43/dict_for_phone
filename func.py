import json



import requests
from googletrans import Translator

token = '6118490871:AAGTVlmAw3-a12tkEy8N9W6gXl2ofmD_8FU'
chat_id = '5274223669'
app_id = 2


def get_list_value(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
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
        result.pronunciation
        return result.text
    except:
        return word


def dictionary_txt():
    dictionary = {}
    with open('dictionary.txt', 'r', encoding='utf-8') as file:
        all_text = file.read().split('\n')[:20]
        for string in all_text:
            string = string.replace('"', '').replace('ˈ', '`').replace('ː', ':').replace('ˌ', '').split(';')
            dictionary[string[0]] = {'translation': string[-1].split(","), 'pronunciations': string[-2] if
            len(string) == 3 else ''}

        return dictionary


# def handle_message(update, context):
#     message = update.message.text
#     sender_id = update.message.from_user.id
#     sender_username = update.message.from_user.username
#     print("Получено сообщение:", message)
#     print("Получено сообщение от пользователя:", sender_username)
#     print("ID пользователя:", sender_id)



if __name__ == '__main__':
    import socket
    from threading import Thread

    # server's IP address
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 5002  # port we want to use
    separator_token = "<SEP>"  # we will use this to separate the client name & message
    # initialize list/set of all connected client's sockets
    client_sockets = set()
    # create a TCP socket
    s = socket.socket()
    # make the port as reusable port
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the address we specified
    s.bind((SERVER_HOST, SERVER_PORT))
    # listen for upcoming connections
    s.listen(5)
    print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
