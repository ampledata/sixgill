#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Constants for SixGill."""

__author__ = 'Greg Albrecht <gba@orionlabs.io>'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'


import logging


LOG_LEVEL = logging.DEBUG
LOG_FORMAT = logging.Formatter(
    '%(asctime)s %(levelname)s %(name)s.%(funcName)s:%(lineno)d'
    ' - %(message)s')

SERIAL_TIMEOUT = 0.01
READ_BYTES = 1000
GPS_WARM_UP = 5

# Cell Number
# ARFCN: Absolute Radio Frequency Channel number
# RXL: Receive Level
# RXQ: Receive Quality
# MCC: Mobile Country Code
# MNC: Mobile Network Code
# BSIC: Base Station Identity Code
# CELLID: Cell ID
# LAC: Location Area Code
# RLA: Receive Level Access Minimum
# TXP: Transmit Power Maximum CCCH
# TA: Timing Advance
CENG_PROPERTIES = [
    'arfcn',
    'rxl',
    'rxq',
    'mcc',
    'mnc',
    'bsic',
    'cell_id',
    'lac',
    'rla',
    'txp',
    'ta'
]
