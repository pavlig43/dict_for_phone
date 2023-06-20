from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem, MDList
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton
from kivy.properties import NumericProperty
from kivy.metrics import dp
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from functools import partial
from kivymd.uix.dialog import MDDialog
import json
from func import get_list_value, tg_message
import requests
from kivymd.uix.pickers import MDColorPicker
from kivymd.theming import ThemeManager





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
                        self.hint_text = hint_text
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


class ItemDrawer(OneLineIconListItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        self.color_picker = MDColorPicker(size_hint=(0.45, 0.85), text_button_cancel = "C")


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
                                              #text_color=self.theme_cls.primary_color,
                                              on_release=self.add_folder
                                          ),
                                          MDFlatButton(
                                              text="Отмена",
                                              theme_text_color="Custom",
                                              #text_color=self.theme_cls.primary_color,
                                              on_release=lambda x: self.dialog_folder.dismiss()
                                          ),
                                      ],
                                      )

    def open_dialog(self, *args):
        self.dialog_folder.open()

    def add_folder(self, *args):
        folder_name = self.dialog_folder.content_cls.ids.folder_dialog_text.text
        folder_dict = self.ids.folder_list.folders
        if folder_name in folder_dict:
            message_error = MDDialog(text='Папка с таким именем уже существует',
                                     buttons=[MDFlatButton(
                                         text='ОК',
                                         on_release=lambda x: message_error.dismiss()
                                     )])
            message_error.open()
        else:
            folder_dict[folder_name] = {}
            item = ItemDrawer(icon='folder', text=folder_name, screen_name=folder_name)
            with open('folders.json', 'w') as f:
                json.dump(folder_dict, f)
            self.ids.folder_list.add_widget(item)
            item.bind(on_release=self.ids.folder_list.to_eximine)
            self.dialog_folder.content_cls.ids.folder_dialog_text.text = ''
            self.dialog_folder.dismiss()




class FolderList(MDList):
    def __init__(self, folders=[], **kwargs):
        super().__init__(**kwargs)
        self.folders = get_list_value('folders.json')
        for folder in list(self.folders):
            item = ItemDrawer(icon='folder', text=folder, screen_name=folder)
            item.bind(on_release=self.to_eximine)
            self.add_widget(item)

    def to_eximine(self, instance):
        sm = self.parent.parent.parent.parent

        try:
            sm.get_screen(instance.screen_name)
        except:

            eximine_screen = Eximine(name=instance.screen_name, name_folder=instance.screen_name)
            sm.add_widget(eximine_screen)


        sm.current = instance.screen_name


class EximineList(MDList):
    def __init__(self, modules=[],name_folder='', **kwargs):
        super().__init__(**kwargs)
        self.name_folder = name_folder
        self.modules = get_list_value('folders.json')[self.name_folder]

        for module in self.modules:
            item = ItemDrawer(icon="school", text=module, screen_name=module)
            item.bind(on_release=self.open_module)
            self.add_widget(item)

    def open_module(self, instance):


        sm = self.parent.parent.parent.parent
        folder = self.parent.parent.parent.parent.parent.name
        module = instance.text
        print(folder, module)
        try:
            sm.get_screen(instance.text)
        except:

            words_screen = Cards(name=instance.text, folder =folder, module=module)
            sm.add_widget(words_screen)


        sm.current = instance.screen_name





class DialogFolder(MDBoxLayout):
    def __init__(self,hint_text = '',**kwargs):
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
                                              #text_color=self.theme_cls.primary_color,
                                              on_release= self.add_module
                                          ),
                                          MDFlatButton(
                                              text="Отмена",
                                              theme_text_color="Custom",
                                              #text_color=self.theme_cls.primary_color,
                                              on_release=lambda x: self.dialog_folder.dismiss()
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
            item = ItemDrawer(icon='school', text=module_name, screen_name=module_name)
            item.bind(on_release=self.eximine_list.open_module)
            self.eximine_list.add_widget(item)
            with open('folders.json', 'r') as f:
                dct = json.load(f)
                dct[self.name_folder] = module_dict
            with open('folders.json', 'w') as f:
                json.dump(dct, f)
            self.dialog_folder.dismiss()

class Cards(MDScreen):
    def __init__(self,folder ='',module='',**kwargs):
        super().__init__(**kwargs)
        self.folder = folder
        self.module = module
        self.ids.name_module.text = f'{self.folder} \n{self.module}'



class DrawerList(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        icons_item = {
            "account-box": {'text': "Профиль", 'screen_name': 'profile'},
            "folder-multiple-outline": {'text': "Мои модули", 'screen_name': 'modules'},
            "school": {'text': "Тестирование", 'screen_name': ''},
            "history": {'text': "Статистика", 'screen_name': ''},
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
    theme_cls =ThemeManager()
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
