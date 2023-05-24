from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty,BooleanProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.theming import ThemableBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import OneLineIconListItem, MDList
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivy.properties import NumericProperty
from kivy.metrics import dp
from kivymd.uix.textfield import MDTextField
from functools import partial



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
                    self.cursor = (0,0)
                    Clock.schedule_once(partial(self.set_cursor, cursor))
        return super(PasswordMDTextField, self).on_touch_down(touch)

    def set_cursor(self, pos, dt):
        self.cursor = pos



class ContentNavigationDrawer(MDBoxLayout):
    pass


class ItemDrawer(OneLineIconListItem):
    icon = StringProperty()
    text_color = ListProperty((0, 0, 0, 1))


class MainMenu(MDScreen):
    pass


class DrawerList(MDList):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        icons_item = {
            "account-box": "Профиль",
            "folder-multiple-outline": "Мои модули",
            "school": "Тестирование",
            "history": "Статистика",
            'file-cog': 'Настройки',
            "gmail": "Связь с разработчиком",
        }
        for icon_name in icons_item.keys():
            item = ItemDrawer(icon=icon_name, text=icons_item[icon_name])
            self.add_widget(item)

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




if __name__ == "__main__":
    Dictionari().run()
