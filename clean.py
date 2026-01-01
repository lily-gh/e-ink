#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import subprocess
import json
import logging
import time
import re
from PIL import Image, ImageDraw, ImageFont

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(libdir):
    sys.path.append(libdir)

import epd7in5b_V2

logging.basicConfig(level=logging.DEBUG)

def main():
    try:
        logging.info("Home Dashboard")

        epd = epd7in5b_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        logging.info("done with Clear")
        epd7in5b_V2.epdconfig.module_exit(cleanup=True)
        exit()


    except IOError as e:
        logging.info(e)
    
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5b_V2.epdconfig.module_exit(cleanup=True)
        exit()

if __name__ == '__main__':
    main()
