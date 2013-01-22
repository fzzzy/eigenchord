
import requests

import time
import sys

import OSC


import Quartz


horiz = True


def light(row, col, light=False):
    if not light:
        requests.delete("http://localhost:1381/column/%s/row/%s" % (row, col)
    )
    else:
        requests.put("http://localhost:1381/column/%s/row/%s" % (row, col), light)


light(1, 4, "orange")
light(1, 7, "green")
light(2, 4, "green")
light(2, 7, "orange")
light(1, 3, "red")
light(2, 3, "orange")
light(3, 1, "green")
light(3, 2, "orange")
light(3, 3, "red")
light(3, 4, "green")


def clear():
    for c in range(2):
        for r in range(9):
            light(c+1, r+1)




class EigenChord(OSC.OSCServer):
    print_tracebacks = True

    x = 640
    y = 400
    previous_x = 640
    previous_y = 400
    click_time = 0
    mouse = False
    mouse_click = False
    right_click = False
    scroll = False
    number = False
    symbol = False
    shift = False
    option = False
    command = False
    control = False
    voices = None

    down_keys = 0
    typed_character = 0

    keys = {
        1: 'click',
##        26: 'rightclick',
        2: 'number',
        11: 'symbol',
        19: 'shift',
        20: 'option',
        21: 'control',
        22: 'command',
        12: 'scroll',
        3: 'mouse',
        99: 'fast_mouse',
    }

    key_numbers = dict(
        (v, k) for (k, v) in keys.items()
    )

    keycodes = {
        'shift': 56,
        'option': 58,
        'command': 55,
        'control': 59,
    }

    chord_keys = {
        4: 1,
        5: 2,
        6: 4,
        7: 8,
        8: 16,
        9: 32,
        16: 1,
        17: 2,
        18: 4,
        13: 8,
        14: 16,
        15: 32,
    }

    chordmap = [
        [999, 31, 34, 2, 45, 37, 32, 51],
        [14, 8, 13, 7, 9, 6, 50, 43],
        [17, 46, 16, 53, 11, 27, 47, 42],
        [1, 40, 125, 39, 33, 999, 999, 999],
        [0, 3, 35, 30, 5, 116, 124, 119],
        [4, 12, 48, 999, 121, 24, 999, 999],
        [15, 38, 126, 999, 123, 999, 41, 999],
        [49, 47, 44, 999, 115, 999, 999, 36],
    ]

    numbers = [18, 19, 20, 21, 23, 22, 26, 28, 25, 29]

    def handle_error(self, request, client_address):
        (e_type, e) = sys.exc_info()[:2]
        if e_type is KeyboardInterrupt:
            self.running = False
            print
        else:
            OSC.OSCServer.handle_error(self, request, client_address)

    def post_scroll(self, x, y):
        Quartz.CGEventPost(
            Quartz.kCGHIDEventTap,
            Quartz.CGEventCreateScrollWheelEvent(
                None,
                Quartz.kCGScrollEventUnitPixel,
                2,
                x,
                y))

    def post_event(self, event_type):
        evt = Quartz.CGEventCreateMouseEvent(
            None,
            event_type,
            Quartz.CGPointMake(int(self.x), int(self.y)),
            Quartz.kCGMouseButtonLeft)
        Quartz.CGEventSetFlags(
            evt, self.get_mask())
        Quartz.CGEventPost(
            Quartz.kCGHIDEventTap, evt)

    def mouse_down(self, vel):
        print "mouse"
        self.mouse = True
        #if vel > 0.5:
        #    print "click"
        #    self.mouse_click = True
        #    self.post_event(Quartz.kCGEventLeftMouseDown)
        #    self.click_time = time.time()

    def mouse_up(self, vel):
        print "no mouse"
        self.mouse = False
        #if self.mouse_click:
        #    self.post_event(Quartz.kCGEventLeftMouseUp)
        #    self.mouse_click = False

    def click_down(self, vel):
        if not self.mouse_click:
            print "click"
            self.mouse_click = True
            self.post_event(Quartz.kCGEventLeftMouseDown)

    def click_up(self, vel):
        if self.mouse_click:
            print "no click"
            self.post_event(Quartz.kCGEventLeftMouseUp)
            self.mouse_click = False

    def rightclick_down(self, vel):
        print "right click"
        self.right_click = True
        self.post_event(Quartz.kCGEventRightMouseDown)

    def rightclick_up(self, vel):
        print "no right click"
        self.right_click = False
        self.post_event(Quartz.kCGEventRightMouseUp)

    def scroll_down(self, vel):
        print "scroll"
        self.scroll = True

    def scroll_up(self, vel):
        print "no scroll"
        self.scroll = False

    def number_down(self, vel):
        print "number"
        self.number = True

    def number_up(self, vel):
        print "no number"
        self.number = False

    def symbol_down(self, vel):
        print "symbol"
        self.symbol = True

    def symbol_up(self, vel):
        print "no symbol"
        self.symbol = False

    def number_event(self, evt_name, key, vel):
        if (key < 4 or (key > 9 and key < 13) or key > 16):
            return
        if key > 9:
            key -= 3
        keycode = self.numbers[key - 4]
        print "code", key, keycode, evt_name
        evt = Quartz.CGEventCreateKeyboardEvent(
            None, keycode, evt_name == 'down')
        Quartz.CGEventSetFlags(
            evt, self.get_mask())
        Quartz.CGEventPost(
            Quartz.kCGHIDEventTap,
            evt)

    def symbol_event(self, evt_name, key, vel):
        self.shift = True
        self.number_event(evt_name, key, vel)
        self.shift = False

    def get_mask(self):
        mask = 0
        if self.shift:
            mask += Quartz.kCGEventFlagMaskShift
        elif self.option:
            mask += Quartz.kCGEventFlagMaskAlternate
        elif self.command:
            mask += Quartz.kCGEventFlagMaskCommand
        elif self.control:
            mask += Quartz.kCGEventFlagMaskControl
#        print "mask", mask            
        return mask

    def key_event(self, evt_name, key, vel):
        key_name = self.keys.get(key, None)

        func = getattr(self, '%s_%s' % (key_name, evt_name), None)
        if func is not None:
            print key_name, evt_name
            func(vel)
            return

        if key_name is not None:
            print "modifier", key_name, evt_name
            keycode = self.keycodes[key_name]
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                    Quartz.CGEventCreateKeyboardEvent(
                        None, keycode, evt_name == 'down'))
            setattr(self, key_name, evt_name == 'down')
            return

        chord_factor = self.chord_keys.get(key, None)
        if chord_factor:
            print "chord", chord_factor, evt_name
            if evt_name == 'down':
                self.down_keys |= chord_factor
                self.typed_character |= chord_factor
            else:
                self.down_keys &= ~chord_factor
                if not self.down_keys:
                    typed, self.typed_character = self.typed_character, 0
                    outer, inner = typed >> 3, typed & 7
                    typed = self.chordmap[inner][outer]
                    if typed is 999:
                        return
                    down = Quartz.CGEventCreateKeyboardEvent(
                        None, typed, 1)
                    Quartz.CGEventSetFlags(
                        down, self.get_mask())
                    Quartz.CGEventPost(
                        Quartz.kCGHIDEventTap,
                            down)
                    time.sleep(0.125)
                    Quartz.CGEventPost(
                        Quartz.kCGHIDEventTap,
                            Quartz.CGEventCreateKeyboardEvent(
                                None, typed, 0))
            return

        print "undefined key", key, evt_name

    def message(self, pattern, tags, data, client_address):
        if data[0] == ".":
            return ## ignore breath

        #print pattern, tags, data

        if self.voices is None:
            self.voices = {}

        voice = pattern.split('/')[-1]
        if voice in self.voices:
            key = self.voices[voice]
            if not (self.key_numbers['mouse'] == key or self.key_numbers['scroll'] == key):
                if data[0]:
                    return
                evt_name = 'up'
                self.voices.pop(voice)
                vel = 0
            else:
                evt_name = "cursor"
                vel = 1.0
        else:
            evt_name = 'down'
            key = int(data[0])
            self.voices[voice] = key
            if len(data) < 8:
                vel = 1.0
            else:
                vel = data[7]

        if key != self.key_numbers['number'] and self.number:
            self.number_event(evt_name, key, vel)
        elif key != self.key_numbers['symbol'] and self.symbol:
            self.symbol_event(evt_name, key, vel)
        elif evt_name != "cursor":
            self.key_event(evt_name, key, vel)
        else:
            if self.mouse:
                if self.click_time:
                    if time.time() - self.click_time > 0.25:
                        self.click_time = 0
                    else:
                        print "clicktime"

                if self.click_time:
                    return

                if key == self.key_numbers['mouse'] or key == self.key_numbers['fast_mouse']:
                    if key == self.key_numbers['mouse']:
                        scale = 10
                    else:
                      scale = 20
                    xamt = data[-2]
                    yamt = data[-1]
                    if abs(xamt) > 0.1:
                        if horiz:
                            self.x += xamt * scale
                        else:
                            self.y += xamt * scale
                        #print 'yaw', xamt

                    if abs(yamt) > 0.1:
                        if horiz:
                            self.y += -scale * yamt
                        else:
                            self.x += -scale * yamt
                        #print 'roll', yamt

                    if self.x < 0:
                        self.x = 0
                    if self.x > 840:
                        self.x = 840
                    if self.y < 0:
                        self.y = 0
                    if self.y > 525:
                        self.y = 525

                    evt = Quartz.kCGEventMouseMoved
                    if self.mouse_click:
                        evt = Quartz.kCGEventLeftMouseDragged
                    elif self.right_click:
                        evt = Quartz.kCGEventRightMouseDragged
                    self.post_event(evt)

            elif self.scroll:
                if key == self.key_numbers['scroll']:
                    xamt = data[-2]
                    yamt = data[-1]

                    if abs(xamt) > 0.1:

                        #print "scroll x", param
                        if horiz:
                            self.post_scroll(0, -xamt * 5)
                        else:
                            self.post_scroll(-xamt * 5, 0)

                    if abs(yamt) > 0.1:

                        #print "scroll y", param
                        if horiz:
                            self.post_scroll(yamt * 5, 0)
                        else:
                            self.post_scroll(0, yamt * 5)

        return

server = EigenChord(('127.0.0.1', 4442))
server.addMsgHandler('default', server.message)
client = OSC.OSCClient()
client.connect(('127.0.0.1', 9999))
msg = OSC.OSCMessage("/register-fast")
msg.append("keyboard_1")
msg.append(4442)
client.send(msg)

print "EigenChord listening on 127.0.0.1:4442"

try:
    server.serve_forever()
except KeyboardInterrupt:
    print

