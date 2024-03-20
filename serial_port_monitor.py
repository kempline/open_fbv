import os
import sys
import time
import logging
log = logging.getLogger(__name__)
from threading import Timer


class SerialPortMonitor:
    POLLING_INTERVAL_IN_SEC = 1
    UBS_SERIAL_HOME = '/dev/tty.usbserial-'

    def __init__(self):
        self.known_serial_devices = list()
        self.serial_device_available_cb = None
        self.serial_device_unplugged_cb = None
        self.monitor_serial_ports_timer = Timer(1, self.monitor)
        self.monitor_serial_ports_timer.start()

    def monitor(self):
        if sys.platform != 'darwin':
            log.warning('monitoring of serial ports only implemented for Darwin OS')
            return

        log.info('Waiting for serial interface to be connected!')

        while True:
            current_serial_devices = self.get_ftdi_devices()

            for known_serial_device in self.known_serial_devices:
                device_found = False
                for current_serial_device in current_serial_devices:
                    if current_serial_device['USB Serial Number'] == known_serial_device:
                        device_found = True
                    break
                if device_found is False:
                    if self.serial_device_unplugged_cb is not None:
                        self.serial_device_unplugged_cb(self.UBS_SERIAL_HOME + known_serial_device)
                    self.known_serial_devices.remove(known_serial_device)

            for serial_device in current_serial_devices:
                usb_serial = serial_device['USB Serial Number']
                if usb_serial not in self.known_serial_devices:
                    if self.serial_device_available_cb is not None:
                        full_device_path = self.UBS_SERIAL_HOME + usb_serial
                        if os.path.exists(full_device_path):
                            self.serial_device_available_cb(self.UBS_SERIAL_HOME + usb_serial)
                            self.known_serial_devices.append(usb_serial)
                        else:
                            log.info('device not mounted yet - will try later!')
            time.sleep(self.POLLING_INTERVAL_IN_SEC)

    @staticmethod
    def get_ftdi_devices():
        FTDI_VENDOR_ID = '1027'
        FTDI_PRODUCT_ID = ['24577']

        ftdi_device = False
        usb_params = list()
        found_devices = list()
        out = os.popen("ioreg -p IOUSB -w0 -l").read()
        lines = out.splitlines()
        ftdi_params = dict()
        for line in lines:
            trimmed_line = line.replace('|', '').strip()
            if trimmed_line.startswith('+-o '):
                device_summary_line = trimmed_line[4:]
                ftdi_params['summary'] = device_summary_line

            elif trimmed_line.startswith('{'):
                if ftdi_device is True:
                    pass # process
                    ftdi_device = False
                usb_params = list()
            elif trimmed_line.startswith('}'):
                if ftdi_device is True:

                    for line in usb_params:
                        name, var = line.partition("=")[::2]
                        name = name.replace('"', '').strip()
                        name = name.replace('|', '').strip()
                        var = var.replace('"', '').strip()
                        if name == '{' or name == '}':
                            continue
                        ftdi_params[name] = var
                    try:
                        if ftdi_params['idProduct'] in FTDI_PRODUCT_ID:
                            found_devices.append(ftdi_params)
                        ftdi_params = dict()
                        ftdi_device = False
                    except KeyError as _e:
                        pass
                usb_params = list()
            elif 'idVendor" = ' + FTDI_VENDOR_ID in line:
                ftdi_device = True
            usb_params.append(trimmed_line)
        return found_devices
