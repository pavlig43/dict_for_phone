import pyttsx3
from kivy.animation import Animation
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen

from func import speaker


class RepCardScreen(MDScreen):
    def __init__(self, dictionary={}, **kwargs):
        super().__init__(**kwargs)

        self.dict_unknown = {}
        self.dictionary = dictionary
        self.number = 0
        self.engine = pyttsx3.init()

        self.engine.setProperty('rate', 150)

        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)

        try:
            first_card = list(self.dictionary.keys())[self.number]
            self.ids.word_label.text = first_card
            self.ids.pronunciations_label.text = self.dictionary[first_card]['pronuncation']
            self.ids.def_label.text = ','.join(self.dictionary[first_card]['definition'])
            self.ids.counter.text = f'{self.number + 1}/{str(len(self.dictionary))}'
        except IndexError:
            self.dialog = MDDialog(text='В этом модуле нет слов',
                                   buttons=[MDFlatButton(text='OK',
                                                         on_release=lambda x: (
                                                             self.dialog.dismiss(),
                                                             self.back()))])
            self.dialog.open()

    def next_card(self, known=True, *args):
        self.number += 1
        if not known:
            self.dict_unknown[list(self.dictionary.keys())[self.number - 1]] \
                = self.dictionary[list(self.dictionary.keys())[self.number - 1]]
        try:
            self.ids.word_card.opacity = 1
            self.ids.def_card.opacity = 0

            next_card = list(self.dictionary.keys())[self.number]
            self.ids.word_label.text = next_card
            self.ids.pronunciations_label.text = self.dictionary[next_card]['pronuncation']
            self.ids.def_label.text = ','.join(self.dictionary[next_card]['definition'])
            self.ids.counter.text = f'{self.number + 1}/{str(len(self.dictionary))}'



        except IndexError:
            if self.dict_unknown:
                self.dialog = MDDialog(text=f"Повторить незнакомые слова {len(self.dict_unknown)}",
                                       buttons=[MDFlatButton(text="ОК", on_release=lambda x: (
                                           self.dialog.dismiss(), self.repeat())),
                                                MDFlatButton(text="Нет", on_release=lambda x: (
                                                    self.dialog.dismiss(), self.back()))])
                self.dialog.open()
            else:
                self.back()

    def repeat(self, *args):
        sm = self.parent
        self.parent.remove_widget(self)
        rep_card_screen = RepCardScreen(name='rep_card_screen', dictionary=self.dict_unknown)
        sm.add_widget(rep_card_screen)
        sm.current = 'rep_card_screen'

    def back(self):
        sm = self.parent
        sm.current = self.parent.previous()
        self.parent.remove_widget(self)

    def audio(self, text, *args):
        self.engine.say(text)
        self.engine.runAndWait()


class RepCardWord(MDCardSwipe):

    def __init__(self, *args, **kwargs):

        super().__init__(args, kwargs)

    def open_card(self) -> None:
        if self.type_swipe == "hand":
            swipe_x = (
                self.max_opened_x
                if self.anchor == "left"
                else -self.max_opened_x
            )
        else:
            swipe_x = self.width if self.anchor == "left" else 0
        anim = Animation(
            x=swipe_x, t=self.opening_transition, d=self.opening_time
        )
        anim.bind(on_complete=self._on_swipe_complete)
        anim.start(self.children[0])
        self.state = "opened"

    def on_touch_up(self, touch):
        if self.parent.parent.parent.ids.volume.collide_point(*touch.pos):
            return True
        self._distance = 0
        if self.collide_point(touch.x, touch.y):
            if not self._to_closed:
                self._opens_process = False
                self.complete_swipe()

            if abs(touch.osx - touch.sx) < 0.1:
                self.reverse_card()

            elif touch.osx < touch.sx:
                point_known = int(self.parent.parent.parent.ids.point_known.text)
                point_known += 1
                self.parent.parent.parent.ids.point_known.text = str(point_known)
                swipe_x = self.width

                anim = Animation(
                    x=swipe_x, t=self.opening_transition, d=self.opening_time
                )
                anim += Animation(
                    x=0, t=self.opening_transition, d=self.opening_time)
                anim.start(self)
                self.state = "opened"
                self.parent.parent.parent.next_card()

            else:

                if self.parent.parent.parent.ids.def_card.opacity == 1:
                    swipe_x = self.width
                    anim = Animation(
                        x=-swipe_x, t=self.opening_transition, d=self.opening_time
                    )
                    anim += Animation(
                        x=0, t=self.opening_transition, d=self.opening_time)
                    anim.start(self.parent.parent.parent.ids.def_card)
                    self.state = "opened"
                point_unknown = int(self.parent.parent.parent.ids.point_unknown.text)
                point_unknown += 1
                self.parent.parent.parent.ids.point_unknown.text = str(point_unknown)
                self.parent.parent.parent.next_card(known=False)
        return super().on_touch_up(touch)

    def reverse_card(self, *args):
        if self.opacity == 1:
            anim = Animation(opacity=0, duration=0.2, )

            anim.start(self)
            self.parent.parent.parent.ids.def_card.opacity = 1
        else:
            anim = Animation(opacity=0, duration=0.2, )

            anim.start(self.parent.parent.parent.ids.def_card)

            self.opacity = 1


class Test(MDApp):
    theme_cls = ThemeManager()

    def build(self):
        self.theme_cls.primary_palette = "Pink"
        return Builder.load_file('repcardscreen.kv')


if __name__ == '__main__':
    Test().run()
