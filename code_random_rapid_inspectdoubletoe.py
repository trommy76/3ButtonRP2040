# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
import time
import random
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

kbd = Keyboard(usb_hid.devices)


def make_button(pin):
    b = digitalio.DigitalInOut(pin)
    b.direction = digitalio.Direction.INPUT
    b.pull = digitalio.Pull.UP
    return b


f8_btn = make_button(board.A2)   # rapid-fire F8 / double-press I
f7_btn = make_button(board.A3)   # F7
f9_btn = make_button(board.A1)   # F9

# ---- Tuning (seconds) ----
DOUBLE_PRESS_WINDOW = 2.0
F8_HOLD_MIN, F8_HOLD_MAX = 0.040, 0.090   # how long F8 stays down
F8_GAP_MIN,  F8_GAP_MAX  = 0.030, 0.085   # pause between presses
F8_LONG_PAUSE_CHANCE = 0.05               # 5% of gaps get an extra pause
F8_LONG_PAUSE_MIN, F8_LONG_PAUSE_MAX = 0.08, 0.16
I_TAP_MIN, I_TAP_MAX = 0.04, 0.07

last_press_time = None
prev_down = False
suppress_f8 = False

f8_pressed = False
next_f8_time = 0.0

f7_pressed = False
f9_pressed = False


def next_hold():
    return random.uniform(F8_HOLD_MIN, F8_HOLD_MAX)


def next_gap():
    gap = random.uniform(F8_GAP_MIN, F8_GAP_MAX)
    if random.random() < F8_LONG_PAUSE_CHANCE:
        gap += random.uniform(F8_LONG_PAUSE_MIN, F8_LONG_PAUSE_MAX)
    return gap


while True:
    now = time.monotonic()
    down = not f8_btn.value

    # ---- F8 button: rapid F8, or a single I on a double press ----
    if down and not prev_down:
        if last_press_time is not None and (now - last_press_time) <= DOUBLE_PRESS_WINDOW:
            # make sure F8 isn't held before tapping I
            if f8_pressed:
                kbd.release(Keycode.F8)
                f8_pressed = False
            kbd.press(Keycode.I)
            time.sleep(random.uniform(I_TAP_MIN, I_TAP_MAX))
            kbd.release(Keycode.I)
            suppress_f8 = True
            last_press_time = None
        else:
            suppress_f8 = False
            last_press_time = now
            next_f8_time = now          # fire the first F8 immediately

    if down and not suppress_f8:
        if now >= next_f8_time:
            if f8_pressed:
                kbd.release(Keycode.F8)
                f8_pressed = False
                next_f8_time = now + next_gap()
            else:
                kbd.press(Keycode.F8)
                f8_pressed = True
                next_f8_time = now + next_hold()
    else:
        if f8_pressed:
            kbd.release(Keycode.F8)
            f8_pressed = False

    if not down:
        suppress_f8 = False

    prev_down = down

    # ---- F7 button ----
    f7_down = not f7_btn.value
    if f7_down and not f7_pressed:
        kbd.press(Keycode.F7)
        f7_pressed = True
    elif not f7_down and f7_pressed:
        kbd.release(Keycode.F7)
        f7_pressed = False

    # ---- F9 button ----
    f9_down = not f9_btn.value
    if f9_down and not f9_pressed:
        kbd.press(Keycode.F9)
        f9_pressed = True
    elif not f9_down and f9_pressed:
        kbd.release(Keycode.F9)
        f9_pressed = False

    time.sleep(0.001)
