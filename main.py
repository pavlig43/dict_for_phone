from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty

from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem, MDList





class LoginWindow(MDBoxLayout):
    pass

class ContentNavigationDrawer(MDBoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


class DrawerList( MDList):
    def set_color_item(self, instance_item):
        """Called when tap on a menu item."""

        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color



class Dictionari(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Pink"
        return Builder.load_file('dictionary.kv')

    def on_start(self):
        icons_item = {
            "account-box": "Профиль",
            "folder-multiple-outline": "Мои модули",
            "school": "Тестирование",
            "history": "Статистика",
            'file-cog': 'Настройки',
            "gmail": "Связь с разработчиком",
        }
        for icon_name in icons_item.keys():
            self.root.ids.content_drawer.ids.md_list.add_widget(
                ItemDrawer(icon=icon_name, text=icons_item[icon_name])
            )

if __name__ == "__main__":
    Dictionari().run()
