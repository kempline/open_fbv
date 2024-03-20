from __future__ import print_function
import sys
import os
import time
from open_fbv import *
import getopt
from serial_interface import SerialIoInterface
from serial_port_monitor import SerialPortMonitor
import logging
log = logging.getLogger(__name__)

ON = 0x01
OFF = 0x00

open_fbv = OpenFbv(None)
last_serial_port = ''
serial_interface = None
serial_port_monitor = None


def switch_channel_leds(val):
    open_fbv.switch_led(FBV.BANK_DOWN, val)
    open_fbv.switch_led(FBV.BANK_UP, val)
    open_fbv.switch_led(FBV.CHANNEL_A, val)
    open_fbv.switch_led(FBV.CHANNEL_B, val)
    open_fbv.switch_led(FBV.CHANNEL_C, val)
    open_fbv.switch_led(FBV.CHANNEL_D, val)


def switch_all_leds(val):
    open_fbv.switch_led(FBV.BANK_DOWN, val)
    open_fbv.switch_led(FBV.BANK_UP, val)
    open_fbv.switch_led(FBV.CHANNEL_A, val)
    open_fbv.switch_led(FBV.CHANNEL_B, val)
    open_fbv.switch_led(FBV.CHANNEL_C, val)
    open_fbv.switch_led(FBV.CHANNEL_D, val)
    open_fbv.switch_led(FBV.FAV_CHANNEL, val)
    open_fbv.switch_led(FBV.AMP1, val)
    open_fbv.switch_led(FBV.AMP2, val)
    open_fbv.switch_led(FBV.REVERB, val)
    open_fbv.switch_led(FBV.TREMOLO, val)
    open_fbv.switch_led(FBV.MODULATION, val)
    open_fbv.switch_led(FBV.DELAY, val)
    open_fbv.switch_led(FBV.TAP_TEMPO, val)
    open_fbv.switch_led(FBV.FX_LOOP, val)
    open_fbv.switch_led(FBV.STOMP_BOX1, val)
    open_fbv.switch_led(FBV.STOMP_BOX2, val)
    open_fbv.switch_led(FBV.STOMP_BOX3, val)
    open_fbv.switch_led(FBV.PEDAL1_GREEN, val)
    open_fbv.switch_led(FBV.PEDAL1_RED, val)
    open_fbv.switch_led(FBV.PEDAL2_GREEN, val)
    open_fbv.switch_led(FBV.PEDAL2_RED, val)


def switch_callback(id, val):
    log.info('switch: ' + str(id) + ', value: ' + str(val))
    if val == 0:
        return
    
    if id == FBV.BANK_DOWN:
        return
    elif id == FBV.BANK_UP:
        return
    elif id == FBV.CHANNEL_A:
        switch_channel_leds(OFF)
        open_fbv.switch_led(id, ON)
        return
    elif id == FBV.CHANNEL_B:
        switch_channel_leds(OFF)
        open_fbv.switch_led(id, ON)
        return
    elif id == FBV.CHANNEL_C:
        switch_channel_leds(OFF)
        open_fbv.switch_led(id, ON)
        return
    elif id == FBV.CHANNEL_D:
        switch_channel_leds(OFF)
        open_fbv.switch_led(id, ON)
        return
    elif id == FBV.FAV_CHANNEL:
        return
    elif id == FBV.AMP1:
        return
    elif id == FBV.AMP2:
        return
    elif id == FBV.REVERB:
        return
    elif id == FBV.TREMOLO:
        return
    elif id == FBV.MODULATION:
        return
    elif id == FBV.DELAY:
        return
    elif id == FBV.TAP_TEMPO:
        return
    elif id == FBV.FX_LOOP:
        return
    elif id == FBV.STOMP_BOX1:
        return
    elif id == FBV.STOMP_BOX2:
        return
    elif id == FBV.STOMP_BOX3:
        return
    elif id == FBV.PEDAL1_GREEN:
        return
    elif id == FBV.PEDAL1_RED:
        return
    elif id == FBV.PEDAL2_GREEN:
        return
    elif id == FBV.PEDAL2_RED:
        return
    else:
       log.warn('switch_callback: unknown switch id: ' + str(id))


def switch_hold_callback(id):
    log.info('switch hold: ' + str(id))


def switch_double_click_callback(id):
    log.info('switch double clicked: ' + str(id))


def pedal_callback(id, val):
    log.info('pedal: ' + str(id) + ' moved: ' + str(val))


def initialize_fbv_callback():
    global open_fbv
    open_fbv.pprint('open fbv rocks!')
    open_fbv.pprint_short(' 123')


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


def notify(title, text):
    os.system("""
              osascript -e 'display notification "{}" with title "{}"'
              """.format(text, title))


def on_serial_exception(exc):
    global open_fbv
    global serial_interface
    global last_serial_port
    if serial_interface is not None:
        open_fbv.stop()
        serial_interface.close()
        notify("open_fbv_tester", "DISCONNECTED from: " + last_serial_port)


def connect_serial(serial_port):
    global open_fbv
    global serial_interface
    global last_serial_port

    serial_interface = SerialIoInterface()
    if serial_interface.connect(serial_device=serial_port) != 0:
        log.error('Connect to serial port: ' + str(serial_port))
        return False

    log.info('Connected to serial port: ' + serial_port)
    serial_interface.serial_exception_cb = on_serial_exception

    open_fbv.set_io_interface(serial_interface)

    open_fbv.register_switch_click_cb(switch_callback)
    open_fbv.register_switch_double_click_cb(switch_double_click_callback)
    open_fbv.register_switch_hold_cb(switch_hold_callback)
    open_fbv.register_pedal_move_cb(pedal_callback)
    open_fbv.register_init_cb(initialize_fbv_callback)

    open_fbv.begin()
    last_serial_port = serial_port
    notify("open_fbv_tester", "Connected to: " + last_serial_port)
    initialize_fbv_callback()
    return True


def main(argv):
    logging.basicConfig(
        level='INFO',
        format="%(asctime)s - %(levelname)s - %(message)s (%(name)s)",
        datefmt="%Y-%m-%d %H:%M:%S")

    global open_fbv
    global serial_port_monitor
    try:
        serial_port = sys.argv[1]
    except IndexError as _:
        serial_port = None

    if serial_port is None:
        notify("open_fbv_tester", "Waiting for serial USB device!" + last_serial_port)
        serial_port_monitor = SerialPortMonitor()
        serial_port_monitor.serial_device_available_cb = connect_serial

    else:
        if os.path.exists(serial_port) is False:
            log.error("Given serial port does not exists")
            print_serial_ports()
            print_usage(True)
        else:
            connect_serial(serial_port)

    while True:
        time.sleep(100)


if __name__ == "__main__":
    main(sys.argv)
