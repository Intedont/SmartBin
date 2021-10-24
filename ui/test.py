import kivy
from kivy.uix.floatlayout import FloatLayout
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.layout import Layout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.uix.image import Image
from kivy.properties import NumericProperty

class FirstWindow(Screen):
    pass

class SecondWindow(Screen):
    pass

class RotationableImage(Image):
    angle = NumericProperty(0)
    def __init__(self, **kwargs):
        super(RotationableImage, self).__init__(**kwargs)
        anim = Animation(angle = -360, duration=4) 
        anim += Animation(angle = -360, duration=4)
        anim.repeat = True
        anim.start(self)
    
    def on_angle(self, item, angle):
        if angle == -360:
            item.angle = 0


class WindowManager(ScreenManager):
    pass 

kv = Builder.load_file('windows.kv')

class TestApp(App):
    def build(self):
        return kv

    def sorting(self):
        print("ssssssss")

if __name__ == '__main__':
    TestApp().run()