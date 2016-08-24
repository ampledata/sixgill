#!/usr/bin/env python


import Queue
import logging
import time

import sixgill


PORT = '/dev/ttyAMA0'
SPEED = '115200'


def main():
    queue = Queue.Queue()

    reader = sixgill.SixGill(port=PORT, speed=SPEED, queue=queue)

    try:
        reader.start()

        queue.join()

        while reader.is_alive():
            time.sleep(0.01)
    except KeyboardInterrupt:
        reader.stop()
    finally:
        reader.stop()


if __name__ == '__main__':
    main()
