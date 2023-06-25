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


def a():
    from kivy.lang import Builder
    from kivy.properties import StringProperty

    from kivymd.app import MDApp
    from kivymd.uix.card import MDCardSwipe

    class AX(MDCardSwipe):
        text = StringProperty()

    class Example(MDApp):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Orange"
            self.screen = Builder.load_file('ax.kv')

        def build(self):
            return self.screen

        def remove_item(self, instance):
            self.screen.ids.md_list.remove_widget(instance)

        def on_start(self):
            for i in range(20):
                self.screen.ids.md_list.add_widget(
                    AX(text=f"One-line item {i}")
                )

    Example().run()


if __name__ == '__main__':
    a()
