import sys
from binascii import hexlify
from threading import Timer
import getopt
import os
import time
# from open_fbv.serial_interface import SerialIoInterface
import logging
log = logging.getLogger(__name__)

ON = 0x01
OFF = 0x00


# noinspection PyClassHasNoInit
class FBV:
    BANK_DOWN = 0x00
    BANK_UP = 0x10
    CHANNEL_A = 0x20
    CHANNEL_B = 0x30
    CHANNEL_C = 0x40
    CHANNEL_D = 0x50
    FAV_CHANNEL = 0x60
    AMP1 = 0x01
    AMP2 = 0x11
    REVERB = 0x21
    TREMOLO = 0x31
    MODULATION = 0x41
    DELAY = 0x51
    TAP_TEMPO = 0x61
    FX_LOOP = 0x02
    STOMP_BOX1 = 0x12
    STOMP_BOX2 = 0x22
    STOMP_BOX3 = 0x32
    PEDAL1_SWITCH = 0x43
    PEDAL1_GREEN = 0x03
    PEDAL1_RED = 0x13
    PEDAL2_SWITCH = 0x53
    PEDAL2_GREEN = 0x23
    PEDAL2_RED = 0x33
    NO_COLOR = 0x00
    WHITE = 0x01
    RED = 0x02
    GREEN = 0x03
    DARK_BLUE = 0x04
    LIGHT_BLUE = 0x05
    YELLOW = 0x06
    PURPLE = 0x07
    ORANGE = 0x08
    PINK = 0x09
    CHANNEL_SWITCHES = [CHANNEL_A, CHANNEL_B, CHANNEL_C, CHANNEL_D, BANK_DOWN, BANK_UP]
    LEDs = CHANNEL_SWITCHES + [FAV_CHANNEL, AMP1, AMP2, REVERB, TREMOLO, MODULATION, DELAY, TAP_TEMPO, FX_LOOP,
                               STOMP_BOX1, STOMP_BOX2, STOMP_BOX3, PEDAL1_GREEN, PEDAL1_RED, PEDAL2_GREEN, PEDAL2_RED]


class FbvSwitchEvent:
    last_preset_switch_id = 0x00

    def __init__(self, switch_id, value):
        self.switch_id = switch_id
        self.value = value


class OpenFbv:
    def __init__(self, p_io_interface):
        self.io_interface = p_io_interface
        self.DISPLAY_SIZE = 16
        self.switch_click_cb_list = list()
        self.paired_switch_click_cb_list = list()
        self.switch_double_click_cb_list = list()
        self.switch_hold_cb_list = list()
        self.pedal_move_cb_list = list()
        self.init_requested_cb_list = list()
        self.display_text_change_cb_list = list()
        self.short_display_text_change_cb_list = list()
        self.led_status_change_cb_list = list()
        self.led_color_change_cb_list = list()
        self.switch_double_click_timer = Timer(0.5, self.double_click_callback)
        self.switch_hold_timer = Timer(3, self.hold_timer_callback)
        self.previous_switch_id = None
        self.data_in = bytearray()
        self.write_to_main_display_command = bytearray([0xf0, 0x13, 0x10, 0x00, 0x10])
        self.main_display_text = bytearray(b"                ")
        self.segment_ids = bytearray([0x09, 0x0a, 0x0b, 0x0c])
        # self.keep_alive_timer = Timer(2, self.send_alive_msg)
        self.alive_signal_from_board_owing = False

        if self.io_interface is not None:
            self.io_interface.register_data_in_callback_fct(self.process_data_in)

        self.switch_history = list()
        # from open_fbv.remote_display.server import Server
        # self.remote_display = Server(self)
        # self.remote_display.start('en0')

    def set_io_interface(self, io_interface):
        self.io_interface = io_interface
        if self.io_interface is not None:
            self.io_interface.register_data_in_callback_fct(self.process_data_in)

    # runs in own thread
    def send_alive_msg(self):
        if self.alive_signal_from_board_owing is True:
            log.warning('No connection to any foot controller')

        # log.info('Fbv Sent alive')
        self.send_data(bytearray([0xf0, 0x02, 0x01, 0x00]))
        self.alive_signal_from_board_owing = True
        self.keep_alive_timer = Timer(2, self.send_alive_msg)
        self.keep_alive_timer.start()

    def signal_communication_start(self):
        self.send_data(bytearray([0xf0, 0x03, 0x31, 0x02, 0x40]))

    def send_data(self, data):
        if self.io_interface is not None:
            self.io_interface.send_data(data)
        else:
            log.warning('Given IO Interface in openFBV class is None - unable to send data')

    def process_data_in(self, p_byte_in):
        if p_byte_in == 0xF0:
            self.data_in = bytearray()
        self.data_in.append(p_byte_in)

        in_length = len(self.data_in)
        if in_length > 32:
            log.warning('Critical buffer filling level on fbv serial in: ' + str(in_length))
            self.data_in = bytearray()
            in_length = 0

        if in_length < 2:
            return

        # 1 start byte (0xF0) and 1 for the length-byte of the message (self.data_in[1])
        if self.data_in[0] == 0xF0:
            if in_length == (self.data_in[1] + 2):
                try:
                    cmd = self.data_in[2]
                    if cmd == 0x90:
                        log.warning('Fbv Board requests reconfiguration')
                        self.initialize_event()
                    elif cmd == 0x80:
                        # log.warning('Fbv is alive')
                        self.alive_signal_from_board_owing = False
                    elif cmd == 0x81:
                        self.switch_event(self.data_in[3], self.data_in[4])
                    elif cmd == 0x82:
                        self.pedal_event(self.data_in[3], self.data_in[4])
                    else:
                        out_str = ''
                        for b in self.data_in:
                            out_str += str(b) + ' '
                        log.warning('Unknown cmd received from FBV: ' + out_str)
                        self.data_in = bytearray()
                        in_length = 0

                except IndexError:
                    log.error(
                        'IndexError. Data is: ' + str(self.data_in) + ', in_length: ' + str(in_length) + ' - ' +
                        str(self.data_in[1]))
                    for b in self.data_in:
                        print(str(b))
        else:
            self.data_in = bytearray()

    def begin(self):
        self.signal_communication_start()
        # self.keep_alive_timer.start()

    def stop(self):
        self.keep_alive_timer.cancel()
        self.io_interface = None

    def pprint(self, message):
        # log.info('Msg for main display: ' + message)
        for i in range(0, 16):
            try:
                self.main_display_text[i] = int(hexlify(str.encode(message[i])), 16)
            except IndexError:
                self.main_display_text[i] = 0x20
        self.send_data(self.write_to_main_display_command)
        self.send_data(self.main_display_text)

        for cb in self.display_text_change_cb_list:
            cb(message)

    def send_raw(self, raw_message):
        self.send_data(raw_message)

    def pprint_short(self, message):
        fbv3_msg = bytearray([0xf0, 0x05, 0x08, 0x20, 0x20, 0x20, 0x20])
        for i in range(0, 4):
            try:
                val = int(hexlify(str.encode(message[i])), 16)
                self.send_data(bytearray([0xf0, 0x02, self.segment_ids[i], val]))
                fbv3_msg[i + 3] = val
            except IndexError:
                self.send_data(bytearray([0xf0, 0x02, self.segment_ids[i], 0x20]))
        self.send_data(fbv3_msg)

        for cb in self.short_display_text_change_cb_list:
            cb(message)

    def set_led_color(self, hardware_id, color_idx):
        if color_idx < FBV.NO_COLOR or color_idx > FBV.PINK:
            log.warning('Color index for LED not in range 0..9: ' + str(color_idx))
            color_idx = FBV.NO_COLOR

        data = bytearray([0xF0, 0x03, 0x05, hardware_id, color_idx])
        self.send_data(data)
        for cb in self.led_color_change_cb_list:
            cb(hardware_id, color_idx)

    def switch_led(self, hardware_id, state):
        if hardware_id == FBV.PEDAL1_SWITCH:
            self.send_data(bytearray([0xF0, 0x03, 0x04, FBV.PEDAL1_GREEN, not state]))
            self.send_data(bytearray([0xF0, 0x03, 0x04, FBV.PEDAL1_RED, state]))
        elif hardware_id == FBV.PEDAL2_SWITCH:
            self.send_data(bytearray([0xF0, 0x03, 0x04, FBV.PEDAL2_GREEN, not state]))
            self.send_data(bytearray([0xF0, 0x03, 0x04, FBV.PEDAL2_RED, state]))
        else:
            data = bytearray([0xF0, 0x03, 0x04, hardware_id, state])
            self.send_data(data)

        for cb in self.led_status_change_cb_list:
            cb(hardware_id, state)

    def show_accidential(self, state):
        data = bytearray([0xF0, 0x02, 0x20, state])
        self.send_data(data)

    def switch_double_click_event(self, switch_id):
        if len(self.switch_double_click_cb_list) == 0:
            log.warning("No callback fct registered for switch_double_click_event so far.")
        else:
            for cb in self.switch_double_click_cb_list:
                cb(switch_id)

    def check_paired_switch_evt(self, switch_id, val):
        if switch_id in [FBV.CHANNEL_A, FBV.CHANNEL_B, FBV.CHANNEL_C, FBV.CHANNEL_D]:
            FbvSwitchEvent.last_preset_switch_id = switch_id

        if switch_id == 1 and val == 0:
            previous_evt = self.switch_history[-1]
            for cb in self.paired_switch_click_cb_list:
                cb(previous_evt.switch_id)
            self.switch_history = list()

        self.switch_history.append(FbvSwitchEvent(switch_id, val))

        history_len = len(self.switch_history)
        if history_len >= 4:
            last_four_switches = []
            for i in range(history_len-4, history_len):
                last_four_switches.append(self.switch_history[i].value)
            if last_four_switches == [1, 0, 0, 0]:
                for cb in self.paired_switch_click_cb_list:
                    cb(FbvSwitchEvent.last_preset_switch_id)
                self.switch_history = list()

        # limit size of history
        self.switch_history = self.switch_history[:6]

    def switch_event(self, switch_id, val):
        self.check_paired_switch_evt(switch_id, val)

        # log.info("switch event: switch=" + str(id) + ', value=' + str(val))
        if len(self.switch_click_cb_list) == 0:
            log.warning("No callback fct registered for switch event so far.")
        else:
            for cb in self.switch_click_cb_list:
                cb(switch_id, val)

        if val == 0:
            self.switch_hold_timer.cancel()
            self.switch_hold_timer = Timer(3, self.hold_timer_callback)
        else:
            double_click_timer_alive = self.switch_double_click_timer.is_alive()
            self.switch_double_click_timer.cancel()
            self.switch_double_click_timer = Timer(0.5, self.double_click_callback)

            # FBV.TAP_TEMPO for Express board.
            if double_click_timer_alive and switch_id in [self.previous_switch_id, FBV.TAP_TEMPO]:
                self.switch_double_click_event(self.previous_switch_id)
            else:
                self.switch_double_click_timer.start()
            self.previous_switch_id = switch_id

            # hold timer
            if self.switch_hold_timer.is_alive() is True:
                self.switch_hold_timer.cancel()
                self.switch_hold_timer = Timer(3, self.hold_timer_callback)
            self.switch_hold_timer.start()

    def initialize_event(self):
        # start identifier for settings
        self.send_data(bytearray([0xf0, 0x01, 0x40]))
        self.signal_communication_start()

        if len(self.init_requested_cb_list) == 0:
            log.warning("No callback fct registered for init-request event so far.")
        else:
            for cb in self.init_requested_cb_list:
                cb()

        # end identifier for settings
        self.send_data(bytearray([0xf0, 0x01, 0x41]))

        # do not know exactly the meanings. Found by re-engineering.
        # But these values are important for the FBV #3 to start sending keep-alive messages
        self.send_data(bytearray([0xf0, 0x02, 0x01, 0x00]))
        self.send_data(bytearray([0xf0, 0x02, 0x01, 0x01]))

    def double_click_callback(self):
        self.switch_double_click_timer = Timer(0.5, self.double_click_callback)

    def hold_timer_callback(self):
        if len(self.switch_hold_cb_list) == 0:
            log.warning("No callback fct registered for hold_timer_callback so far.")
        else:
            for cb in self.switch_hold_cb_list:
                cb(self.previous_switch_id)

        self.switch_hold_timer = Timer(3, self.hold_timer_callback)

    def pedal_event(self, pedal_id, val):
        if len(self.pedal_move_cb_list) == 0:
            log.warning("No callback fct registered for pedal_event so far.")
        else:
            for cb in self.pedal_move_cb_list:
                cb(pedal_id, val)

    def register_switch_click_cb(self, cb):
        self.switch_click_cb_list.append(cb)

    def register_paired_switch_click_cb(self, cb):
        self.paired_switch_click_cb_list.append(cb)

    def register_switch_double_click_cb(self, cb):
        self.switch_double_click_cb_list.append(cb)

    def register_switch_hold_cb(self, cb):
        self.switch_hold_cb_list.append(cb)

    def register_pedal_move_cb(self, cb):
        self.pedal_move_cb_list.append(cb)

    def register_init_cb(self, cb):
        self.init_requested_cb_list.append(cb)

    def register_display_text_change(self, cb):
        self.display_text_change_cb_list.append(cb)

    def register_short_display_text_change(self, cb):
        self.short_display_text_change_cb_list.append(cb)

    def register_led_status_change(self, cb):
        self.led_status_change_cb_list.append(cb)

    def register_led_color_change(self, cb):
        self.led_color_change_cb_list.append(cb)

    @staticmethod
    def generate_tuner_msg(value):
        '''
              ))))
               )))
                ))
                  ****
                      ((
                      (((
                      ((((
        '''
        # clean = [0xF0, 19, 0x10, 0x00, 0x10, ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        msg = [0xF0, 19, 0x10, 0x00, 0x10]
        if value < 1:
            # generate empty tuner message that will turn off all LEDs
            pass
        elif value < 15:
            for c in '  ))))':
                msg.append(ord(c))
        elif value < 31:
            for c in '   )))':
                msg.append(ord(c))
        elif value < 47:
            for c in '    ))':
                msg.append(ord(c))
        elif value < 79:
            for c in '      ****':
                msg.append(ord(c))
        elif value < 95:
            for c in '          ((':
                msg.append(ord(c))
        elif value < 113:
            for c in '          (((':
                msg.append(ord(c))
        elif value <= 127:
            for c in '          ((((':
                msg.append(ord(c))
        else:
            log.warn('value not between 0...127: ' + str(value))
            return list()

        while len(msg) < 21:
            msg.append(ord(' '))
        msg = msg[:21]
        return msg

    @staticmethod
    def get_serial_ports():
        import glob
        if sys.platform == 'darwin':
            return glob.glob('/dev/tty.usbserial-*')


class OpenFbvTester:
    def __init__(self):
        self.open_fbv = None

    def switch_channel_leds(self, val):
        self.open_fbv.switch_led(FBV.BANK_DOWN, val)
        self.open_fbv.switch_led(FBV.BANK_UP, val)
        self.open_fbv.switch_led(FBV.CHANNEL_A, val)
        self.open_fbv.switch_led(FBV.CHANNEL_B, val)
        self.open_fbv.switch_led(FBV.CHANNEL_C, val)
        self.open_fbv.switch_led(FBV.CHANNEL_D, val)

    def switch_all_leds(self, val):
        self.open_fbv.switch_led(FBV.BANK_DOWN, val)
        self.open_fbv.switch_led(FBV.BANK_UP, val)
        self.open_fbv.switch_led(FBV.CHANNEL_A, val)
        self.open_fbv.switch_led(FBV.CHANNEL_B, val)
        self.open_fbv.switch_led(FBV.CHANNEL_C, val)
        self.open_fbv.switch_led(FBV.CHANNEL_D, val)
        self.open_fbv.switch_led(FBV.FAV_CHANNEL, val)
        self.open_fbv.switch_led(FBV.AMP1, val)
        self.open_fbv.switch_led(FBV.AMP2, val)
        self.open_fbv.switch_led(FBV.REVERB, val)
        self.open_fbv.switch_led(FBV.TREMOLO, val)
        self.open_fbv.switch_led(FBV.MODULATION, val)
        self.open_fbv.switch_led(FBV.DELAY, val)
        self.open_fbv.switch_led(FBV.TAP_TEMPO, val)
        self.open_fbv.switch_led(FBV.FX_LOOP, val)
        self.open_fbv.switch_led(FBV.STOMP_BOX1, val)
        self.open_fbv.switch_led(FBV.STOMP_BOX2, val)
        self.open_fbv.switch_led(FBV.STOMP_BOX3, val)
        self.open_fbv.switch_led(FBV.PEDAL1_GREEN, val)
        self.open_fbv.switch_led(FBV.PEDAL1_RED, val)
        self.open_fbv.switch_led(FBV.PEDAL2_GREEN, val)
        self.open_fbv.switch_led(FBV.PEDAL2_RED, val)

    def switch_callback(self, switch_id, val):
        log.info('switch: ' + str(switch_id) + ', value: ' + str(val))
        if val == 0:
            return

        if switch_id == FBV.BANK_DOWN:
            return
        elif switch_id == FBV.BANK_UP:
            return
        elif switch_id in FBV.CHANNEL_SWITCHES:
            self.switch_channel_leds(OFF)
            self.open_fbv.switch_led(switch_id, ON)
            return
        elif switch_id == FBV.FAV_CHANNEL:
            return
        elif switch_id == FBV.AMP1:
            return
        elif switch_id == FBV.AMP2:
            return
        elif switch_id == FBV.REVERB:
            return
        elif switch_id == FBV.TREMOLO:
            return
        elif switch_id == FBV.MODULATION:
            return
        elif switch_id == FBV.DELAY:
            return
        elif switch_id == FBV.TAP_TEMPO:
            return
        elif switch_id == FBV.FX_LOOP:
            return
        elif switch_id == FBV.STOMP_BOX1:
            return
        elif switch_id == FBV.STOMP_BOX2:
            return
        elif switch_id == FBV.STOMP_BOX3:
            return
        elif switch_id == FBV.PEDAL1_GREEN:
            return
        elif switch_id == FBV.PEDAL1_RED:
            return
        elif switch_id == FBV.PEDAL2_GREEN:
            return
        elif switch_id == FBV.PEDAL2_RED:
            return
        else:
            log.warning('switch_callback: unknown switch id: ' + str(switch_id))

    @staticmethod
    def switch_hold_callback(switch_id):
        log.info('switch hold: ' + str(switch_id))

    @staticmethod
    def switch_double_click_callback(switch_id):
        log.info('switch double clicked: ' + str(switch_id))

    @staticmethod
    def pedal_callback(pedal_id, val):
        log.info('pedal: ' + str(pedal_id) + ' moved: ' + str(val))

    def initialize_fbv_callback(self, ):
        self.open_fbv.pprint('open fbv rocks!')
        self.open_fbv.pprint_short(' 123')

    def run_test(self, serial_port='', remote_display_network_interface=None):
        open_fbv_raw_interface = SerialIoInterface()
        if open_fbv_raw_interface.server_loop(serial_device=serial_port) != 0:
            log.error('Connect to serial port: ' + str(serial_port))
            sys.exit(0)

        self.open_fbv = OpenFbv(open_fbv_raw_interface)

        self.open_fbv.register_switch_click_cb(self.switch_callback)
        self.open_fbv.register_switch_double_click_cb(self.switch_double_click_callback)
        self.open_fbv.register_switch_hold_cb(self.switch_hold_callback)
        self.open_fbv.register_pedal_move_cb(self.pedal_callback)
        self.open_fbv.register_init_cb(self.initialize_fbv_callback)

        self.open_fbv.begin()

        self.initialize_fbv_callback()

        # start remote display
        if remote_display_network_interface is not None:
            self.open_fbv.remote_display.start(remote_display_network_interface)

        while True:
            time.sleep(100)


def print_usage(p_b_exit=True):
    print("Usage: %s [serial_port]" % sys.argv[0])
    print()
    if p_b_exit is True:
        sys.exit(1)


def print_serial_ports():
    serial_ports = OpenFbv.get_serial_ports()
    log.info("Available ports are: ")
    for port in serial_ports:
        log.info('\t' + port)
    log.info('')


def main():
    remote_desktop_wlan_if = None
    serial_port = None
    try:
        options, args = getopt.getopt(sys.argv[1:], "s:w:h:")
        for opt, arg in options:
            if opt in '-h':
                print_usage()
            elif opt in '-s':
                serial_port = arg
            elif opt in '-w':
                remote_desktop_wlan_if = arg
            else:
                print_usage()
    except getopt.GetoptError as e:
        print(str(e))
        print_usage(True)

    if serial_port is None:
        log.error("No serial port provided")
        print_serial_ports()
        print_usage(True)

    if os.path.exists(serial_port) is False:
        log.error("Given serial port does not exists")
        print_serial_ports()
        print_usage(True)

    open_fbv_tester = OpenFbvTester()
    open_fbv_tester.run_test(serial_port, remote_desktop_wlan_if)


if __name__ == "__main__":
    main()
