"""
    cloudplayer.iokit.channel
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2018 by the cloudplayer team
    :license: Apache-2.0, see LICENSE for details
"""
from cloudplayer.iokit.component import Component
from cloudplayer.iokit.channel import Input


class RotaryEncoder(Component):
    """Rotaion encoder, that is a composite component made up of two inputs.
    Based on the phase they are triggered in, a rotation direction can be
    inferred.
    """

    ROTATE_LEFT = 'ROTATE_LEFT'
    ROTATE_RIGHT = 'ROTATE_RIGHT'

    def __init__(self, clk, dt):
        super().__init__()
        self.clk = Input(clk)
        self.dt = Input(dt)
        self.clk.subscribe(Input.VALUE_CHANGED, self.clk_changed)
        self.dt.subscribe(Input.VALUE_CHANGED, self.dt_changed)
        self.last_clk_state = self.clk.get()

    def clk_changed(self, event):
        self.rotate(event.value, self.dt.get())

    def dt_changed(self, event):
        self.rotate(self.clk.get(), event.value)

    def rotate(self, clk_state, dt_state):
        if clk_state != self.last_clk_state:
            self.last_clk_state = clk_state
            if dt_state == clk_state:
                self.publish(RotaryEncoder.ROTATE_LEFT)
            else:
                self.publish(RotaryEncoder.ROTATE_RIGHT)


class Potentiometer(Component):
    """Potentiometer-like abstraction which encloses a rotary encoder.
    A potentiometer has a pre-defined value range, whereas a rotary encoder
    rotates endlessly.
    """

    VALUE_CHANGED = 'VALUE_CHANGED'

    def __init__(self, clk, dt, initial=0.0, steps=32.0):
        super().__init__()
        self.rotary_encoder = rt = RotaryEncoder(clk, dt)
        rt.subscribe(RotaryEncoder.ROTATE_LEFT, self.rotate_left)
        rt.subscribe(RotaryEncoder.ROTATE_RIGHT, self.rotate_right)
        self.value = initial
        self.step = 1.0 / steps

    def rotate_left(self, event):
        self.update_value(self.value - self.step)

    def rotate_right(self, event):
        self.update_value(self.value + self.step)

    def update_value(self, value):
        value = max(min(value, 1.0), 0.0)
        if self.value != value:
            self.value = value
            self.publish(Potentiometer.VALUE_CHANGED, value)
