#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""SixGill Commands."""

__author__ = 'Greg Albrecht <gba@orionlabs.io>'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'
__license__ = 'Apache License, Version 2.0'


import argparse
import Queue
import logging
import time

import sixgill


def cli():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-m', '--modem_port', help='modem_port'
    )
    parser.add_argument(
        '-s', '--modem_speed', help='modem_speed', default=9600
    )
    parser.add_argument(
        '-G', '--gps_port', help='gps_port', required=False
    )
    parser.add_argument(
        '-S', '--gps_speed', help='gps_speed', default=9600
    )
    parser.add_argument(
        '-d', '--debug', help='Enable debug logging', action='store_true'
    )

    opts = parser.parse_args()

    if opts.debug:
        sixgill.constants.LOG_LEVEL = logging.DEBUG
    else:
        sixgill.constants.LOG_LEVEL = logging.INFO

    queue = Queue.Queue()

    if opts.gps_port:
        gps_p = sixgill.SerialGPSPoller(opts.gps_port, opts.gps_speed)
        gps_p._logger.setLevel(sixgill.constants.LOG_LEVEL)
    else:
        gps_p = None

    modem_reader = sixgill.SixGillReader(
        port=opts.modem_port, speed=opts.modem_speed, queue=queue, gps=gps_p)
    modem_reader._logger.setLevel(sixgill.constants.LOG_LEVEL)

    queue_worker = sixgill.SixGillWorker(queue=queue)
    queue_worker._logger.setLevel(sixgill.constants.LOG_LEVEL)

    try:
        if opts.gps_port:
            gps_p.start()
            time.sleep(sixgill.constants.GPS_WARM_UP)
        modem_reader.start()
        queue_worker.start()
        queue.join()

        while modem_reader.is_alive() and queue_worker.is_alive():
            time.sleep(0.01)
    except KeyboardInterrupt:
        if opts.gps_port:
            gps_p.stop()
        modem_reader.stop()
        queue_worker.stop()
    finally:
        if opts.gps_port:
            gps_p.stop()
        modem_reader.stop()
        queue_worker.stop()
