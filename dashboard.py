#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import subprocess
import json
import logging
import time
from PIL import Image, ImageDraw, ImageFont

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(libdir):
    sys.path.append(libdir)

import epd7in5b_V2

logging.basicConfig(level=logging.DEBUG)

def get_tasks():
    """
    Runs todoist.py and returns a list of tasks.
    """
    try:
        process = subprocess.Popen(['python', 'todoist.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            output = stdout.decode('utf-8')
            # The script prints a JSON array at the end, find and parse it
            json_start = output.find('[\n')
            if json_start != -1:
                json_str = output[json_start:]
                return json.loads(json_str)
        else:
            logging.error("Error running todoist.py")
            logging.error(stderr.decode('utf-8'))
            return []
    except Exception as e:
        logging.error(f"Exception getting tasks: {e}")
        return []
    return []

def draw_weather(draw, x_offset, y_offset, width, height, font_large, font_medium):
    """
    Draws the weather pane.
    """
    draw.rectangle([(x_offset, y_offset), (x_offset + width, y_offset + height)], fill=255)
    
    # Placeholders
    current_temp = "15°C"
    min_temp = "10°C"
    max_temp = "20°C"
    location = "Berlin/Schöneberg"

    # Centered current weather
    _, _, w, h = font_large.getbbox(current_temp)
    draw.text((x_offset + (width - w) / 2, y_offset + (height - h) / 2), current_temp, font=font_large, fill=0)

    # Location
    _, _, w_loc, h_loc = font_medium.getbbox(location)
    draw.text((x_offset + (width - w_loc) / 2, y_offset + (height - h) / 2 + h), location, font=font_medium, fill=0)

    # Min and Max weather
    _, _, w_min, h_min = font_medium.getbbox(min_temp)
    draw.text((x_offset + 10, y_offset + (height - h_min) / 2), min_temp, font=font_medium, fill=0)

    _, _, w_max, h_max = font_medium.getbbox(max_temp)
    draw.text((x_offset + width - w_max - 10, y_offset + (height - h_max) / 2), max_temp, font=font_medium, fill=0)

def draw_bus_departures(draw, x_offset, width, height, font_medium):
    """
    Draws the bus departure times pane.
    """
    draw.rectangle([(x_offset, 0), (x_offset + width, height)], fill=255)
    
    title = "Bus 106 Departures"
    _, _, w, h = font_medium.getbbox(title)
    draw.text((x_offset + (width - w) / 2, 10), title, font=font_medium, fill=0)

    # Placeholders for departure times
    departures = ["10:15", "10:30", "10:45"]
    y_pos = 10 + h + 10
    for departure in departures:
        draw.text((x_offset + 20, y_pos), departure, font=font_medium, fill=0)
        _, _, _, text_h = font_medium.getbbox(departure)
        y_pos += text_h + 5

def draw_tasks(draw, x_offset, y_offset, width, height, font_medium, font_small):
    """
    Draws the tasks pane.
    """
    draw.rectangle([(x_offset, y_offset), (x_offset + width, y_offset + height)], fill=255)
    
    title = "Lily's Tasks"
    _, _, w, h = font_medium.getbbox(title)
    draw.text((x_offset + (width - w) / 2, y_offset + 10), title, font=font_medium, fill=0)

    tasks = get_tasks()
    y_pos = y_offset + 10 + h + 10
    if tasks:
        for task in tasks:
            draw.text((x_offset + 20, y_pos), f"- {task}", font=font_small, fill=0)
            _, _, _, task_h = font_small.getbbox(task)
            y_pos += task_h + 5
            if y_pos > y_offset + height - 20: # Don't draw off screen
                break
    else:
        draw.text((x_offset + 20, y_pos), "No tasks today!", font=font_small, fill=0)


def main():
    try:
        logging.info("Home Dashboard")

        epd = epd7in5b_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        logging.info("done with Clear")

        font_large = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 48)
        font_medium = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
        font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

        while True:
            # Create a new image for the display
            Himage = Image.new('1', (epd.width, epd.height), 255)  # Black and white
            Other = Image.new('1', (epd.width, epd.height), 255)   # Red
            draw_bw = ImageDraw.Draw(Himage)
            draw_red = ImageDraw.Draw(Other)

            # Screen dimensions
            screen_width = epd.width
            screen_height = epd.height

            # Vertical split
            left_pane_width = screen_width // 2
            right_pane_width = screen_width // 2

            # Left pane horizontal split
            weather_pane_height = int(screen_height * 0.30)
            
            # Right pane horizontal split
            bus_pane_height = int(screen_height * 0.25)
            tasks_pane_height = screen_height - bus_pane_height

            # Draw Weather (top-left pane)
            draw_weather(draw_bw, 0, 0, left_pane_width, weather_pane_height, font_large, font_medium)

            # Draw Bus Departures (top-right pane)
            draw_bus_departures(draw_bw, left_pane_width, right_pane_width, bus_pane_height, font_medium)

            # Draw Tasks (bottom-right pane)
            draw_tasks(draw_bw, left_pane_width, bus_pane_height, right_pane_width, tasks_pane_height, font_medium, font_small)

            # Draw vertical separator line
            draw_bw.line((left_pane_width, 0, left_pane_width, screen_height), fill=0, width=2)

            epd.display(epd.getbuffer(Himage), epd.getbuffer(Other))
            
            logging.info("Sleeping for 30 minutes...")
            time.sleep(30 * 60)

    except IOError as e:
        logging.info(e)
    
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd7in5b_V2.epdconfig.module_exit(cleanup=True)
        exit()

if __name__ == '__main__':
    main()
