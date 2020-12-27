import os
import time
from kivy.app import App
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, ListProperty
from kivymd.toast import toast
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ThreeLineIconListItem
from threading import Thread
from functools import partial
from kivy.factory import Factory
import concurrent.futures
import json
import screens
import logic

# Keyboard settings:
Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

folder = os.path.dirname(os.path.realpath(__file__))
Builder.load_file("kv/myprogressspinner.kv")
threads = []

class MainApp(MDApp):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.screen_manager = ObjectProperty()
        self.resource_list = ObjectProperty()
        self.opposite_colors = BooleanProperty(True)
        self.screen_list = []
        self.local_id = None
        self.id_token = None
        self.snackbar = None
        self.progressspinner = False
        self.popup = Factory.LoadingPopup()
        self.popup.background = "images/transparent_image.png"
        self.t1 = Thread(target=self.display_loading_screen)
        self.row_data = ListProperty()


    def build(self):
        Clock.max_iteration = 20

    def on_start(self):
        self.screen_manager = self.root.ids.main_screen_manager

        pass

    def change_main_screen(self, new_screen, direction):
        self.screen_manager.transition.direction = direction
        self.screen_manager.current = new_screen

    def night_mode(self):
        if self.theme_cls.theme_style == "Dark":
            self.theme_cls.theme_style = "Light"
        else:
            self.theme_cls.theme_style = "Dark"



    def populate_dataframe(self, area, *args):
        data, df = logic.get_data(area)
        layout = self.root.ids.data_screen.ids.data_screen_layout
        title = self.root.ids.data_screen.ids.data_screen_title
        btn = self.root.ids.data_screen.ids.btn
        search = self.root.ids.data_screen.ids.area_name
        search_card = self.root.ids.data_screen.ids.search_card
        if area != 'all':

            data_tables = MDDataTable(
                size_hint=(0.9, 1),
                pos_hint={'center_x': 0.5},
                use_pagination=True,
                # halign='center',
                column_data=[
                    ("Date", dp(25)),
                    ("New Cases", dp(25)),
                    ("New Deaths", dp(25)),
                ],
                row_data=[(item['date'], item['newCases'], (item['newDeaths'] if item['newDeaths'] else item['newDeathsByPublishDate'])) for item in data['data']],
                rows_num=10)
            title.text = area.title()
        else:
            _all_data_dict = {
                'data': []
            }
            deaths = [deaths for deaths in data['newDeathsByPublishDate'].values()]
            for i, date in enumerate(data['newCases'].keys()):
                _all_data_dict['data'].append({
                    'date': date,
                    'newCases': data['newCases'][date],
                    'newDeaths': data['newDeaths'][date]
                })
                _all_data_dict['newCases'] = data['newCases'][date]
            data_tables = MDDataTable(
                size_hint=(0.9, 1),
                pos_hint={'center_x': 0.5},
                use_pagination=True,
                # halign='center',
                column_data=[
                    ("Date", dp(25)),
                    ("New Cases", dp(25)),
                    ("New Deaths", dp(25)),
                ],
                row_data=[(item['date'],
                           item['newCases'],
                           item['newDeaths']) for item in list(reversed(_all_data_dict['data']))],
                rows_num=10
            )
            title.text = 'Data for the Whole United Kingdom'

        layout.clear_widgets()
        layout.add_widget(title)
        layout.add_widget(data_tables)
        layout.add_widget(search_card)
        spacer = MDLabel(
            size_hint_y=None,
            height=0.05
        )
        layout.add_widget(spacer)

        # try:
        #     for t in threads:
        #         t.join()
        # except RuntimeError as r:
        #     print(r)
        Clock.schedule_once(self.hide_loading_screen)

    def dataframe_callback(self):
        self.display_loading_screen()
        t = Thread(target=self.dataframe_thread)
        t.daemon = True
        t.start()
        threads.append(t)

    def dataframe_thread(self, *args):
        area = self.root.ids.data_screen.ids.area_name
        if area.text:
            self.populate_dataframe(area.text)
        else:
            area.hint_text = 'You must write something'
            # try:
            #     for t in threads:
            #         t.join()
            # except RuntimeError as r:
            #     print(r)
            Clock.schedule_once(self.hide_loading_screen)
            Clock.schedule_once(lambda dt: self.reset_hint_text(), 2)

    def reset_hint_text(self):
        self.root.ids.data_screen.ids.area_name.hint_text = 'Area'


    def display_loading_screen(self, *args):
        self.progressspinner = True
        self.popup.color = self.theme_cls.bg_light
        self.popup.open()

    def hide_loading_screen(self, *args):
        self.progressspinner = False
        self.popup.dismiss()

    def callback(self):
        toast('Coming soon')


if __name__ == "__main__":
    MainApp().run()