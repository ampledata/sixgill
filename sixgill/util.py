#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utilities for the SixGill."""

__author__ = 'Greg Albrecht <gba@orionlabs.io>'
__license__ = 'Apache License, Version 2.0'
__copyright__ = 'Copyright 2016 Orion Labs, Inc.'


import sixgill.constants


def parse_ceng(ceng):
    _ceng = ceng.replace('+CENG: 0,', '').replace('"', '').rstrip()
    return dict(zip(sixgill.constants.CENG_PROPERTIES, _ceng.split(',')))


def run_doctest():  # pragma: no cover
    """Runs doctests for this module."""
    import doctest
    import sixgill.util  # pylint: disable=W0406,W0621
    return doctest.testmod(sixgill.util)


if __name__ == '__main__':
    run_doctest()  # pragma: no cover
