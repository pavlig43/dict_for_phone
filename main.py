from kivy.lang import Builder
import random
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem, MDList, OneLineAvatarIconListItem
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.properties import NumericProperty
from kivy.metrics import dp
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard, MDCardSwipe
from functools import partial
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
import json
from func import get_list_value, tg_message, dictionary_txt, translate_word
from cardswipe import RepCardScreen
import requests
from kivymd.uix.pickers import MDColorPicker
from kivymd.theming import ThemeManager
from kivymd.uix.selectioncontrol import MDCheckbox


class LoginWindow(MDScreen):
    pass


class PasswordMDTextField(MDTextField):
    password_mode = BooleanProperty(True)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.icon_right:
                # icon position based on the KV code for MDTextField
                icon_x = (self.width + self.x) - (self._icon_right_label.texture_size[1]) - dp(8)
                icon_y = self.center[1] - self._icon_right_label.texture_size[1] / 2
                if self.mode == "rectangle":
                    icon_y -= dp(4)
                elif self.mode != 'fill':
                    icon_y += dp(8)

                # not a complete bounding box test, but should be sufficient
                if touch.pos[0] > icon_x and touch.pos[1] > icon_y:
                    if self.password_mode:
                        self.icon_right = 'eye'
                        self.password_mode = False
                        self.password = self.password_mode
                    else:
                        self.icon_right = 'eye-off'
                        self.password_mode = True
                        self.password = self.password_mode

                    # try to adjust cursor position
                    cursor = self.cursor
                    self.cursor = (0, 0)
                    Clock.schedule_once(partial(self.set_cursor, cursor))
        return super(PasswordMDTextField, self).on_touch_down(touch)

    def set_cursor(self, pos, dt):
        self.cursor = pos


class ContentNavigationDrawer(MDBoxLayout):
    pass


class ItemDrawer(OneLineAvatarIconListItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    icon_right = StringProperty()
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))
    screen_name = StringProperty()

    def set_color_item(self):
        """Called when tap on a menu item."""

        # Set the color of the icon and text for the menu item.
        for item in self.parent.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        self.text_color = self.theme_cls.primary_color


class MainMenu(MDScreen):
    pass


class Setting(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_picker = MDColorPicker(size_hint=(0.45, 0.85), text_button_cancel="C")

    def open_pick(self):
        self.color_picker.open()


class Profile(MDScreen):
    pass


class Modules(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dialog_folder = MDDialog(type="custom",
                                      content_cls=DialogFolder(hint_text='Название папки'),
                                      buttons=[
                                          MDFlatButton(
                                              text="Добавить",
                                              theme_text_color="Custom",
                                              # text_color=self.theme_cls.primary_color,
                                              on_release=self.add_folder
                                          ),
                                          MDFlatButton(
                                              text="Отмена",
                                              theme_text_color="Custom",
                                              # text_color=self.theme_cls.primary_color,
                                              on_release=lambda x: self.dialog_folder.dismiss()
                                          ),
                                      ],
                                      )
        self.message_warning = MDDialog(type="custom",
                                        content_cls=MDLabel(text=f'Удалить?'),
                                        buttons=[
                                            MDFlatButton(
                                                text="Да",
                                                theme_text_color="Custom",
                                                # text_color=self.theme_cls.primary_color,

                                            ),
                                            MDFlatButton(
                                                text="Отмена",
                                                theme_text_color="Custom",
                                                # text_color=self.theme_cls.primary_color,
                                                on_release=lambda x: self.message_warning.dismiss()
                                            ),
                                        ],
                                        )

    def open_dialog(self, *args):
        self.dialog_folder.open()

    def add_folder(self, *args):
        folder_name = self.dialog_folder.content_cls.ids.folder_dialog_text.text
        self.folder_dict = self.ids.folder_list.folders
        if folder_name in self.folder_dict:
            message_error = MDDialog(text='Папка с таким именем уже существует',
                                     buttons=[MDFlatButton(
                                         text='ОК',
                                         on_release=lambda x: message_error.dismiss()
                                     )])
            message_error.open()
        else:
            self.folder_dict[folder_name] = {}
            item = ItemDrawer(icon='folder', text=folder_name, screen_name=folder_name, icon_right='delete')
            with open('folders.json', 'w') as f:
                json.dump(self.folder_dict, f)
            self.ids.folder_list.add_widget(item)
            item.bind(on_release=self.ids.folder_list.to_eximine)
            item.ids.icon_right.bind(on_release=lambda x, item=item: self.open_warning_dialog(item))
            self.dialog_folder.content_cls.ids.folder_dialog_text.text = ''
            self.dialog_folder.dismiss()

    def open_warning_dialog(self, folder):
        self.message_warning.open()
        self.message_warning.buttons[0].bind(
            on_release=lambda x: (self.delete_folder(folder), self.message_warning.dismiss()))

    def delete_folder(self, folder):

        del self.folder_dict[folder.text]
        with open('folders.json', 'w') as f:
            json.dump(self.folder_dict, f)
        self.ids.folder_list.remove_widget(folder)


class FolderList(MDList):
    def __init__(self, folders=[], **kwargs):
        super().__init__(**kwargs)
        self.folders = get_list_value('folders.json')
        for folder in list(self.folders):
            item = ItemDrawer(icon='folder', text=folder, screen_name=folder, icon_right='delete')
            item.ids.icon_right.bind(on_release=lambda x, item=item: self.open_warning_dialog(item))
            item.bind(on_release=self.to_eximine)
            self.add_widget(item)

    def open_warning_dialog(self, folder):
        message_warning = self.parent.parent.parent.parent.parent.message_warning
        message_warning.open()
        message_warning.buttons[0].bind(
            on_release=lambda x: (self.delete_folder(folder), message_warning.dismiss()))

    def delete_folder(self, folder):
        self.remove_widget(folder)
        del self.folders[folder.text]
        with open('folders.json', 'w') as f:
            json.dump(self.folders, f)

    def to_eximine(self, instance):
        sm = self.parent.parent.parent.parent

        try:
            sm.get_screen(instance.screen_name)
        except:

            eximine_screen = Eximine(name=instance.screen_name, name_folder=instance.screen_name)
            sm.add_widget(eximine_screen)

        sm.current = instance.screen_name


class EximineList(MDList):
    def __init__(self, modules=[], name_folder='', **kwargs):
        super().__init__(**kwargs)
        self.name_folder = name_folder
        self.modules = get_list_value('folders.json')[self.name_folder]

        for module in self.modules:
            item = ItemDrawer(icon="school", text=module, screen_name=module, icon_right='delete')
            item.bind(on_release=self.open_module)
            item.ids.icon_right.bind(on_release=lambda x, item=item: self.open_warning_dialog(item))
            self.add_widget(item)

    def open_warning_dialog(self, module):
        message_warning = self.parent.parent.parent.parent.parent.message_warning
        message_warning.open()
        message_warning.buttons[0].bind(
            on_release=lambda x: (self.delete_folder(module), message_warning.dismiss()))

    def delete_folder(self, module):
        self.remove_widget(module)
        with open('folders.json', 'r') as f:
            dct = json.load(f)
            del dct[self.name_folder][module.text]
        with open('folders.json', 'w') as f:
            json.dump(dct, f)

    def open_module(self, instance):

        sm = self.parent.parent.parent.parent

        folder = self.parent.parent.parent.parent.parent.name
        module = instance.text

        try:
            sm.get_screen(instance.text)
        except:

            cards = Cards(name=instance.text, folder=folder, module=module)
            sm.add_widget(cards)

        sm.current = instance.screen_name


class DialogFolder(MDBoxLayout):
    def __init__(self, hint_text='', **kwargs):
        super().__init__(**kwargs)
        self.hint_text = hint_text
        self.ids.folder_dialog_text.hint_text = self.hint_text


class Eximine(MDScreen):
    def __init__(self, name_folder='', **kwargs):
        super().__init__(**kwargs)
        self.name_folder = name_folder
        self.eximine_list = EximineList(name_folder=self.name_folder, id='eximine_list')
        self.ids.eximine_list_scroll.add_widget(self.eximine_list)
        self.dialog_folder = MDDialog(type="custom",
                                      content_cls=DialogFolder(hint_text='Название модуля '),
                                      buttons=[
                                          MDFlatButton(
                                              text="Добавить",
                                              theme_text_color="Custom",
                                              # text_color=self.theme_cls.primary_color,
                                              on_release=self.add_module
                                          ),
                                          MDFlatButton(
                                              text="Отмена",
                                              theme_text_color="Custom",
                                              # text_color=self.theme_cls.primary_color,
                                              on_release=lambda x: self.dialog_folder.dismiss()
                                          ),
                                      ],
                                      )
        self.message_warning = MDDialog(type="custom",
                                        content_cls=MDLabel(text=f'Удалить?'),
                                        buttons=[
                                            MDFlatButton(
                                                text="Да",
                                                theme_text_color="Custom",
                                                # text_color=self.theme_cls.primary_color,

                                            ),
                                            MDFlatButton(
                                                text="Отмена",
                                                theme_text_color="Custom",
                                                # text_color=self.theme_cls.primary_color,
                                                on_release=lambda x: self.message_warning.dismiss()
                                            ),
                                        ],
                                        )

    def open_dialog(self, *args):
        self.dialog_folder.open()

    def add_module(self, *args):
        module_name = self.dialog_folder.content_cls.ids.folder_dialog_text.text
        module_dict = self.eximine_list.modules
        if module_name in module_dict:
            message_error = MDDialog(text='Модуль с таким именем уже существует',
                                     buttons=[MDFlatButton(
                                         text='ОК',
                                         on_release=lambda x: message_error.dismiss()
                                     )])
            message_error.open()

        else:
            module_dict[module_name] = {}
            item = ItemDrawer(icon='school', text=module_name, screen_name=module_name, icon_right='delete')
            item.bind(on_release=self.eximine_list.open_module)
            item.ids.icon_right.bind(on_release=lambda x, item=item: self.open_warning_dialog(item))
            self.eximine_list.add_widget(item)
            with open('folders.json', 'r') as f:
                dct = json.load(f)
                dct[self.name_folder] = module_dict
            with open('folders.json', 'w') as f:
                json.dump(dct, f)
            self.dialog_folder.dismiss()
        self.dialog_folder.content_cls.ids.folder_dialog_text.text = ''

    def open_warning_dialog(self, module):
        self.message_warning.open()
        self.message_warning.buttons[0].bind(
            on_release=lambda x: (self.delete_folder(module), self.message_warning.dismiss()))

    def delete_folder(self, module):
        self.eximine_list.remove_widget(module)

        with open('folders.json', 'r') as f:
            dct = json.load(f)
            del dct[self.name_folder][module.text]
        with open('folders.json', 'w') as f:
            json.dump(dct, f)


class Cards(MDScreen):
    def __init__(self, folder='', module='', **kwargs):
        super().__init__(**kwargs)
        self.folder = folder
        self.module = module
        self.words = get_list_value('folders.json')[self.folder][self.module]
        self.ids.name_module.text = f'{self.folder} \n{self.module}'

    def change_module_screen(self):
        sm = self.parent
        try:
            sm.get_screen('change_module')
        except:
            self.change_module = ChangeModule(name='change_module', folder=self.folder, module=self.module)
            sm.add_widget(self.change_module)

        for word, info in self.words.items():
            word_def = WordDef(word=word, definition=info['definition'], pronunciation=info['pronuncation'])
            self.change_module.ids.boxlayout_words.add_widget(word_def)
            word_def.ids.word.text = word
            word_def.ids.definition.text = ','.join(info['definition'])
            word_def.ids.pronunciation.text = info['pronuncation']

        sm.current = 'change_module'

    def replace(self, obj):
        obj_list = list(obj.keys())
        random.shuffle(obj_list)

        return {i: obj[i] for i in obj_list}

    def open_dialog(self):
        new_dict = self.replace(self.words)
        self.dial = MDDialog(text='Перемешать слова?',
                             buttons=[MDFlatButton(text='ДА',
                                                   on_release=lambda x: (
                                                       self.cardswipe_screen(self.replace(new_dict)),
                                                       self.dial.dismiss())),
                                      MDFlatButton(text='НЕТ',
                                                   on_release=lambda x: (
                                                       self.cardswipe_screen(self.words), self.dial.dismiss()))])

        self.dial.open()

    def cardswipe_screen(self, dct):

        sm = self.parent

        try:
            sm.get_screen('rep_card_screen')
        except:
            self.rep_card_screen = RepCardScreen(name='rep_card_screen', dictionary=dct)
            sm.add_widget(self.rep_card_screen)
            sm.current = 'rep_card_screen'

    def to_test_screen(self):
        sm = self.parent
        try:
            sm.get_screen('test_screen')
        except:
            self.test_screen = TestScreen(name='test_screen', word_dict=self.replace(self.words))
            sm.add_widget(self.test_screen)
            sm.current = 'test_screen'
        finally:
            pass


class ChangeModule(MDScreen):
    def __init__(self, folder='', module='', **kwargs):
        super().__init__(**kwargs)

        self.words = {}
        self.folder = folder
        self.module = module
        self.ids.name_field.text = self.module

    def add_word(self):
        self.ids.boxlayout_words.add_widget(WordDef())
        self.ids.scroll_word.scroll_to(self.ids.boxlayout_words.children[0])

    def save_data(self):

        self.words = get_list_value('folders.json')
        self.all_words_dict = {}
        for i in self.ids.boxlayout_words.children:
            if i.ids.word.text in self.all_words_dict:
                i.ids.word.text += ' '
            if i.opacity == 1:
                self.all_words_dict[i.ids.word.text] = {'pronuncation': i.ids.pronunciation.text,
                                                        'definition': i.ids.definition.text.split(',')}

        if not self.ids.name_field.text == self.module:
            del self.words[self.folder][self.module]
            self.module = self.ids.name_field.text
        self.words[self.folder][self.module] = self.all_words_dict
        with open('folders.json', 'w', encoding='utf-8') as f:
            json.dump(self.words, f)
        self.back()

    def back(self):
        self.parent.current = self.parent.previous()
        self.parent.remove_widget(self)


class TestScreen(MDScreen):
    def __init__(self, word_dict='', **kwargs):
        super().__init__(**kwargs)
        self.unknown = 0
        self.word_dict = word_dict
        self.all_words = iter(self.word_dict.keys())
        self.all_def = [self.word_dict[word]['definition'] for word in self.word_dict]
        if len(self.all_def) < 4:
            self.all_def += [''] * (4 - len(self.all_def))
        self.next_test()

    def next_test(self, *args):

        try:
            self.ids.def_grid.clear_widgets()
            word = next(self.all_words)
            self.ids.word_label.text = word
            true_def = self.word_dict[word]['definition']
            definitions = random.sample(self.all_def, 4)
            if not true_def in definitions:
                definitions[random.randint(0, 3)] = true_def

            for i in definitions:
                self.ids.def_grid.add_widget(MDRaisedButton(size_hint=(1, 0.25),
                                                            text=','.join(i),
                                                            on_release= lambda x:(
                                                            self.unknown_test(x,true_def),
                                                            self.next_test())))

        except StopIteration:
            self.result_screen =ResultScreen(len(self.word_dict), self.unknown)
            self.parent.add_widget(self.result_screen)
            self.result_screen.name = 'result_screen'
            self.parent.remove_widget(self)
            self.parent.current = 'result_screen'

    def unknown_test(self, instance, true_def):
        if instance.text != ','.join(true_def):
            self.unknown += 1
class ResultScreen(MDScreen):
    def __init__(self,total='', unknown=''):
        super().__init__()
        self.unknown = unknown
        self.total = f'Всего {total}'
        self.ids.unknown.text = f'Неверно {unknown}'
        self.ids.total.text = f'Всего {total}'
    def ok(self):
        self.parent.current = self.parent.previous()
        self.parent.remove_widget(self)

class WordDef(MDBoxLayout):
    def __init__(self, word='', definition='', pronunciation='', **kwargs):
        super().__init__(**kwargs)
        self.word = word
        self.definition = definition
        self.pronunciation = pronunciation

    def del_word(self):
        if self.opacity == 1:
            self.opacity = 0.2
        else:
            self.opacity = 1

    def choice_definition(self, instance):
        self.definition = self.ids.definition.text.split(',')
        if instance not in self.definition:
            self.definition.append(instance)
        self.ids.definition.text = ','.join(self.definition).strip(',')
        self.menu.dismiss()

    def translate_term(self, instance):

        input_user = self.ids.word.text.lower()
        app = MDApp.get_running_app()
        dictionary_txt = app.dictionary_txt

        try:
            definitions = [{'text': definition,
                            'viewclass': 'OneLineListItem',
                            'on_release': lambda d=definition: self.choice_definition(d)} for definition in
                           dictionary_txt[input_user]['translation']]
        except KeyError:
            definition_from_google = translate_word(input_user)
            definitions = [{'text': definition_from_google,
                            'viewclass': 'OneLineListItem',
                            'on_release': lambda d=definition_from_google: self.choice_definition(d)}]
        try:
            self.ids.pronunciation.text = dictionary_txt[input_user]['pronunciations']

        except KeyError:
            pass
        self.menu = MDDropdownMenu(caller=self.ids.definition,
                                   items=definitions,
                                   width_mult=4,
                                   )

        self.menu.open()


class DrawerList(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        icons_item = {
            "account-box": {'text': "Профиль", 'screen_name': 'profile'},
            "folder-multiple-outline": {'text': "Мои модули", 'screen_name': 'modules'},
            "mail": {'text': "Сообщения", 'screen_name': 'history'},
            'file-cog': {'text': 'Настройки', 'screen_name': 'setting'},
            r"C:\Users\user\PycharmProjects\dict_for_phone\telegram.ico": {'text': "Связь с разработчиком",
                                                                           'screen_name': 'contact_developer'},
        }

        for icon_name, icon_info in icons_item.items():
            item = ItemDrawer(icon=icon_name, text=icon_info['text'], screen_name=icon_info['screen_name'])
            item.bind(on_release=self.menu_callback)
            self.add_widget(item)

    def menu_callback(self, instance):
        try:
            app = MDApp.get_running_app()
            app.root.children[0].ids['nav_drawer'].set_state('close')
            main_screen_manager = app.root.children[0].ids['mainscreenmanager']
            if instance.screen_name == 'modules':
                app.reload_modules()

            main_screen_manager.current = instance.screen_name


        except:
            pass


class ContactDeveloper(MDScreen):
    def send_message(self):
        message = self.ids.message.text
        tg_message(message)
        self.ids.message.text = ''


class Dictionari(MDApp):
    dictionary_txt = dictionary_txt()
    theme_cls = ThemeManager()

    def build(self):
        self.theme_cls.primary_palette = "Pink"

        return Builder.load_file('dictionary.kv')

    def reload_modules(self):
        screen_manager = self.root.children[0].ids['mainscreenmanager']
        modules_screen = screen_manager.get_screen('modules')

        screen_manager.remove_widget(modules_screen)

        new_modules_screen = Modules(name='modules')
        screen_manager.add_widget(new_modules_screen)


if __name__ == "__main__":
    Dictionari().run()
