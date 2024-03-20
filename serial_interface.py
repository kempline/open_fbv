import sys
import serial
from binascii import hexlify
import threading
import time
import logging
log = logging.getLogger(__name__)

MIDI_BAUDRATE = 31250


class SerialIoInterface():
    def __init__(self, name=None):
        self.data_in_cb_fct_list = list()
        self.data_out_cb_fct_list = list()
        self.serial_port = None
        self.serial_exception_cb = None

    def connect(self, serial_device=None, baudrate=MIDI_BAUDRATE, pyboard_uart_id=None, drive_enable_pin_id=None):
        try:
            self.serial_port = serial.Serial(port=serial_device, baudrate=baudrate)
            if self.serial_port.port is not None:
                self.data_out_cb_fct_list.append(self.serial_port.write)
                if sys.version_info < (3, 0, 0):
                    _thread.start_new_thread(self.read_data_in, ())
                else:
                    t = threading.Thread(name='serial_io_interface', target=self.read_data_in)
                    t.setDaemon(True)
                    t.start()
            else:
                log.warn('Running without real serial port to FBV')
            return 0
        except serial.SerialException as e:
            log.error('Initialize serial port. msg: ' + str(e))
            return 1

    def close(self):
        try:
            self.serial_port.close()
            return 0
        except serial.SerialException as e:
            log.error('Initialize serial port. msg: ' + str(e))
            return 1

    def send_data(self, p_data):
        try:
            # if self.serial_port.port is not None:
            #    self.serial_port.write(p_data)
            for cb_fct in self.data_out_cb_fct_list:
                cb_fct(p_data)

        except serial.SerialException as e:
            log.error('Exception sending data to serial: ' + str(e))
            if self.serial_exception_cb is not None:
                self.serial_exception_cb(e)
            # os._exit(1)

    def read_data_in(self):
        while True:
            try:
                byte_in = self.serial_port.read()
                byte_in = int(hexlify(byte_in), 16)

                for cb_fct in self.data_in_cb_fct_list:
                    cb_fct(byte_in)
            except serial.SerialException as e:
                log.error('Caught SerialException in message_loop. Message is: ' + str(e))
                if self.serial_exception_cb is not None:
                    self.serial_exception_cb(e)
                # os._exit(1)
                return 1

    def register_data_in_callback_fct(self, p_cb_fct):
        if p_cb_fct is not None:
            self.data_in_cb_fct_list.append(p_cb_fct)

    def register_data_out_callback_fct(self, p_cb_fct):
        if p_cb_fct is not None:
            self.data_out_cb_fct_list.append(p_cb_fct)
