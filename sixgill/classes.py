#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SixGill Core Classes."""

import logging
import threading
import time
import pynmea2
import requests
import serial

import sixgill.constants

__author__ = 'Greg Albrecht <gba@orionlabs.io>'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'


class SixGillReader(threading.Thread):

    """SixGill Object Class."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(sixgill.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(sixgill.constants.LOG_LEVEL)
        _console_handler.setFormatter(sixgill.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, port, speed, queue, gps=None):
        threading.Thread.__init__(self)
        self.port = port
        self.speed = speed
        self.queue = queue
        self.gps = gps
        self.interface = None
        self.daemon = True
        self._stop = threading.Event()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.interface and self.interface.isOpen():
            self.interface.close()

    def __del__(self):
        if self.interface and self.interface.isOpen():
            self.interface.close()

    def stop(self):
        """
        Stop the thread at the next opportunity.
        """
        self._stop.set()

    def stopped(self):
        """
        Checks if the thread is stopped.
        """
        return self._stop.isSet()

    def run(self):
        self._logger.info('Running %s', self)
        self.interface_init()
        self.read()

    def interface_init(self):
        """
        Initializes the Serial device and commits configuration.
        """
        self.interface = serial.Serial(self.port, self.speed)
        self.interface.timeout = sixgill.constants.SERIAL_TIMEOUT

        self._enter_eng_mode()

    def _enter_eng_mode(self):
        cmd = 'AT+CENG=2'
        self.write_cmd(cmd)

    def write_cmd(self, cmd):
        """
        Writes AT Command Codes to attached device.
        """
        self._logger.debug('cmd=%s', cmd)
        return self.interface.write(cmd + "\n")

    def add_queue(self, event):
        self.queue.put(event)

    def read(self, callback=None, readmode=True):
        """
        Reads data from Serial device.

        :param callback: Callback to call with decoded data.
        :param readmode: If False, immediately returns frames.
        :type callback: func
        :type readmode: bool

        :return: List of frames (if readmode=False).
        :rtype: list
        """
        self._logger.debug('callback=%s readmode=%s', callback, readmode)

        read_buffer = ''

        while 1:
            read_data = None
            read_data = self.interface.read(sixgill.constants.READ_BYTES)

            waiting_data = self.interface.inWaiting()
            if waiting_data:
                read_data = ''.join([
                    read_data, self.interface.read(waiting_data)])

            if read_data is not None:
                if '\n' in read_data and '+CENG: 0,' in read_data:
                    split_data = read_data.split('\n')
                    for sd in split_data:
                        if '+CENG: 0,' in sd:
                            data_frame = {
                                'ts': time.time(),
                                'ceng0': sd,
                            }
                            if self.gps is not None:
                                data_frame.update(self.gps.gps_props)
                            self.add_queue(data_frame)


class SixGillWorker(threading.Thread):

    """SixGillWorker Object Class."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(sixgill.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(sixgill.constants.LOG_LEVEL)
        _console_handler.setFormatter(sixgill.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self._stop = threading.Event()

    def __enter__(self):
        return self

    def stop(self):
        """
        Stop the thread at the next opportunity.
        """
        self._stop.set()

    def stopped(self):
        """
        Checks if the thread is stopped.
        """
        return self._stop.isSet()

    def run(self):
        self._logger.info('Running %s', self)

        while not self.stopped():
            event = self.queue.get()
            self._logger.debug('event=%s', event)
            event_details = sixgill.parse_ceng(event['ceng0'])
            event.update(event_details)
            #self.bot.rx_event(event)
            print event
            self.queue.task_done()


class SerialGPSPoller(threading.Thread):

    """Threadable Object for polling a serial NMEA-compatible GPS."""

    NMEA_PROPERTIES = [
        'timestamp',
        'lat',
        'latitude',
        'lat_dir',
        'lon',
        'longitude',
        'lon_dir',
        'gps_qual',
        'mode_indicator',
        'num_sats',
        'hdop',
        'altitude',
        'horizontal_dil',
        'altitude_units',
        'geo_sep',
        'geo_sep_units',
        'age_gps_data',
        'ref_station_id',
        'pos_fix_dim',
        'mode_fix_type',
        'mode',
        'pdop',
        'vdop',
        'fix'
    ]

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(sixgill.constants.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(sixgill.constants.LOG_LEVEL)
        _console_handler.setFormatter(sixgill.constants.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False

    def __init__(self, serial_port, serial_speed):
        threading.Thread.__init__(self)
        self._serial_port = serial_port
        self._serial_speed = serial_speed
        self._stopped = False

        self.gps_props = {}
        for prop in self.NMEA_PROPERTIES:
            self.gps_props[prop] = None

        self._serial_int = serial.Serial(
            self._serial_port, self._serial_speed, timeout=1)

    def stop(self):
        """
        Stop the thread at the next opportunity.
        """
        self._stopped = True
        return self._stopped

    def run(self):
        self._logger.info('Running %s', self)

        streamreader = pynmea2.NMEAStreamReader(self._serial_int)

        try:
            while not self._stopped:
                for msg in streamreader.next():
                    for prop in self.NMEA_PROPERTIES:
                        if getattr(msg, prop, None) is not None:
                            self.gps_props[prop] = getattr(msg, prop)
                            self._logger.debug(
                                '%s=%s', prop, self.gps_props[prop])
        except StopIteration:
            pass
