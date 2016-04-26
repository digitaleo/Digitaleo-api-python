#!/usr/bin/env python
# coding: utf-8

import logging
import sys

FORMAT = '[%(asctime)s] %(module)s %(levelname)s: %(message)s'
logger = logging.getLogger()
formatter = logging.Formatter(FORMAT)

stream_hdlr  = logging.StreamHandler(sys.stdout)
stream_hdlr.setFormatter(formatter)

logger.addHandler(stream_hdlr)
logger.setLevel(logging.INFO)
# Set requests logger to warning
logging.getLogger("requests").setLevel(logging.WARNING)
