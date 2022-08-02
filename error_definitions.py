#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging


class Error(Exception):
    pass


class LogfileNotMade(Error):
    '''
    WARNING: Raised when logfile is missing
    '''
    pass