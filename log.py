#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import logging
import logging.handlers


def add_file_log(p_log, p_filename):
    max_bytes = 5 * 1024 * 1024
    fh = logging.handlers.RotatingFileHandler(p_filename, mode='a', maxBytes=max_bytes, backupCount=1)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    fh.setFormatter(formatter)
    p_log.addHandler(fh)

def setup_logger(p_logger_name):
    # create logger
    logger = logging.getLogger(p_logger_name)
    logger.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")

    # add formatter to ch
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger

log = setup_logger('open_fbv')
