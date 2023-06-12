import json


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




if __name__ == '__main__':
    a = get_list_value('list.json')
    print(a.keys())
