import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
import requests
from datetime import datetime
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

# API መረጃዎች
api_key = "e9a95b77eba7237f2a107a30efca4dbb"
url_fixtures = "https://v3.football.api-sports.io/fixtures?league=39&season=2023"
url_scorers = "https://v3.football.api-sports.io/players/topscorers?league=39&season=2023"
headers = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': api_key
}

KV = '''
BoxLayout:
    orientation: 'vertical'
    md_bg_color: 0.07, 0.07, 0.07, 1

    MDTopAppBar:
        title: "KOKI SCORE PRO"
        anchor_title: "center"
        md_bg_color: 0, 0.8, 0.4, 1
        specific_text_color: 1, 1, 1, 1
        elevation: 2

    MDTabs:
        id: android_tabs
        background_color: 0.12, 0.12, 0.12, 1
        tab_indicator_color: 0, 0.8, 0.4, 1
        tab_hint_text_color: 0.6, 0.6, 0.6, 1

        TabElement:
            title: "የዛሬ ጨዋታዎች"
            ScrollView:
                MDBoxLayout:
                    id: matches_container
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: dp(10)
                    spacing: dp(10)

        TabElement:
            title: "ከፍተኛ ግብ አግቢዎች"
            ScrollView:
                MDBoxLayout:
                    id: scorers_container
                    orientation: 'vertical'
                    adaptive_height: True
                    padding: dp(10)
                    spacing: dp(10)
'''

class TabElement(MDBoxLayout, Screen):
    pass

class KokiScoreApp(MDApp):
    def build(self):
        from kivy.lang import Builder
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        root = Builder.load_string(KV)
        return root

    def on_start(self):
        Clock.schedule_once(self.load_data, 1)

    def load_data(self, *args):
        # እዚህ ጋር ዳታ የመጫን ስራ ይሰራል
        print("ዳታ እየተጫነ ነው...")

if __name__ == '__main__':
    KokiScoreApp().run()
