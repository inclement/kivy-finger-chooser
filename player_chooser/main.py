from __future__ import print_function, division

from kivy.app import App

from kivy.metrics import dp

from kivy.properties import ListProperty, NumericProperty, BooleanProperty

from kivy.animation import Animation
from kivy.animation import *

from kivy.clock import Clock

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

from random import choice

from itertools import cycle
from colorsys import hsv_to_rgb
num_colours = 15
colours = [hsv_to_rgb(hue, 1, 1) for hue in [v / num_colours for v in range(num_colours)]]
colours = colours[::3] + colours[1::3] + colours[2::3]
colours = colours[:1] + colours[2:]
colours = cycle(colours)
print('colours', colours)

touch_circle_size = 40

class ChooserWidget(FloatLayout):
    touches = ListProperty([])
    countdown_start = NumericProperty(3)
    countdown_value = NumericProperty(-1)
    base_font_size = NumericProperty()

    counting_down = BooleanProperty(False)

    def on_touch_down(self, touch):
        super(ChooserWidget, self).on_touch_down(touch)
        print(self.touches)

        tp = TouchPosition(pos=touch.pos)
        tp.colour = next(colours)
        tp.animate_appear()
        self.add_widget(tp)

        self.touches.append(tp)

        touch.ud['tp'] = tp

        if len(self.touches) > 1:
            self.start_countdown()

    def on_touch_move(self, touch):
        touch.ud['tp'].pos = touch.pos

    def on_touch_up(self, touch):
        tp = touch.ud['tp']
        tp.pos = touch.pos
        tp.animate_remove_shrink()
        self.touches.remove(tp)

        if len(self.touches) < 2:
            self.reset_countdown()

    def start_countdown(self):
        if self.counting_down:
            return
        self.countdown_value = self.countdown_start
        Clock.schedule_interval(self.decrement_counter, 1)
        self.ids.countdown_label.throb()
        self.counting_down = True

    def decrement_counter(self, dt):
        self.countdown_value -= 1
        self.ids.countdown_label.throb()
        if self.countdown_value == 0:
            Clock.unschedule(self.decrement_counter)
            self.choose_touch()

    def reset_countdown(self):
        Clock.unschedule(self.decrement_counter)
        self.countdown_value = -1
        self.counting_down = False

    def choose_touch(self):
        touches = self.touches
        touch = choice(touches)

        for other_touch in touches:
            if other_touch is not touch:
                other_touch.animate_fade(0.3)

        touch.animate_fade(1)
        touch.animate_throb()


class CountdownLabel(Label):
    base_font_size = NumericProperty()
    scale = NumericProperty(1)

    def throb(self):

        # anim = Animation(font_size=1.2667*self.base_font_size,
        anim = Animation(scale=1.2667,
                         t='out_sine',
                         duration=0.1)
        anim.bind(on_complete=self._throb_down)
        anim.start(self)

    def _throb_down(self, *args):
        anim = Animation(scale=1.,
                         t='in_sine',
                         duration=0.1)
        anim.start(self)
        

class TouchPosition(Widget):
    colour = ListProperty([0, 0, 0, 1])
    radius = NumericProperty(dp(touch_circle_size))
    opacity = NumericProperty(0.7)
    throbbing = BooleanProperty(False)

    def animate_appear(self):
        self.radius = 0

        anim = Animation(radius=dp(touch_circle_size), duration=0.25,
                         t='out_back')
        anim.start(self)
        
    def animate_remove_shrink(self):
        if self.parent is None:
            raise ValueError('tried to remove TouchPosition but it has no parent')
        self.throbbing = False
        Animation.stop_all(self)
        anim = Animation(radius=0, duration=0.25,
                         t='out_quad')
        anim.bind(on_complete=self.remove_from_parent)
        anim.start(self)

    def remove_from_parent(self, *args):
        self.parent.remove_widget(self)

    def animate_fade(self, opacity=0.4):
        anim = Animation(opacity=opacity, duration=0.6,
                         t='out_expo')
        anim.start(self)

    def animate_throb(self):
        self.throbbing = True
        self._animate_throb_up()

    def _animate_throb_up(self, *args):
        if not self.throbbing:
            return
        anim = Animation(radius=dp(1.333*touch_circle_size),
                         duration=0.4,
                         t='in_out_sine')
        anim.start(self)
        anim.bind(on_complete=self._animate_throb_down)

    def _animate_throb_down(self, *args):
        if not self.throbbing:
            return
        anim = Animation(radius=dp(touch_circle_size),
                         duration=0.4,
                         t='in_out_sine')
        anim.start(self)
        anim.bind(on_complete=self._animate_throb_up)


class PlayerChooserApp(App):
    def build(self):
        return ChooserWidget()

    def on_pause(self):
        return True

if __name__ == "__main__":
    PlayerChooserApp().run()
