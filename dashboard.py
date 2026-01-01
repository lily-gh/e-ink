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

def get_departures():
    """
    Runs departures.py and returns a list of departures.
    """
    try:
        process = subprocess.Popen(['python', 'departures.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            output = stdout.decode('utf-8')
            # The script prints a JSON array at the end, find and parse it
            json_start = output.find('[{')
            if json_start != -1:
                json_str = output[json_start:]
                return json.loads(json_str)
        else:
            logging.error("Error running departures.py")
            logging.error(stderr.decode('utf-8'))
            return []
    except Exception as e:
        logging.error(f"Exception getting departures: {e}")
        return []
    return []

def get_weather():
    """
    Runs weather.py and returns weather data.
    """
    try:
        process = subprocess.Popen(['python', 'weather.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            output = stdout.decode('utf-8')
            # The script prints a JSON object at the end
            json_start = output.find('{')
            if json_start != -1:
                json_str = output[json_start:]
                return json.loads(json_str)
        else:
            logging.error("Error running weather.py")
            logging.error(stderr.decode('utf-8'))
            return None
    except Exception as e:
        logging.error(f"Exception getting weather: {e}")
        return None
    return None

def draw_weather(draw, x_offset, y_offset, width, height, font_large, font_medium, font_small, weather_data):
    """
    Draws the weather pane.
    """
    draw.rectangle([(x_offset, y_offset), (x_offset + width, y_offset + height)], fill=255)
    
    # Show current date at the top
    from datetime import datetime
    font_date = ImageFont.truetype(os.path.join(picdir, 'MapleMonoBold.ttf'), 27)  # 1.5x of font_small (18)
    current_date = datetime.now().strftime("%d %b")
    _, _, date_w, date_h = font_date.getbbox(current_date)
    draw.text((x_offset + (width - date_w) / 2, y_offset + 10), current_date, font=font_date, fill=0)
    
    # Get weather data or use placeholders
    if weather_data and 'now' in weather_data:
        current_temp = f"{weather_data['now']['temp']}°C"
        min_temp = f"{weather_data['now']['min']}°C"
        max_temp = f"{weather_data['now']['max']}°C"
    else:
        current_temp = "--°C"
        min_temp = "--°C"
        max_temp = "--°C"
    
    location = "Berlin/Schöneberg"

    # Centered current weather (adjusted for date above)
    _, _, w, h = font_large.getbbox(current_temp)
    draw.text((x_offset + (width - w) / 2, y_offset + date_h + 20 + (height - date_h - 20 - h) / 2), current_temp, font=font_large, fill=0)

    # Location
    _, _, w_loc, h_loc = font_medium.getbbox(location)
    draw.text((x_offset + (width - w_loc) / 2, y_offset + date_h + 20 + (height - date_h - 20 - h) / 2 + h), location, font=font_medium, fill=0)

    # Min and Max weather
    _, _, w_min, h_min = font_medium.getbbox(min_temp)
    draw.text((x_offset + 10, y_offset + date_h + 20 + (height - date_h - 20 - h_min) / 2), min_temp, font=font_medium, fill=0)

    _, _, w_max, h_max = font_medium.getbbox(max_temp)
    draw.text((x_offset + width - w_max - 10, y_offset + date_h + 20 + (height - date_h - 20 - h_max) / 2), max_temp, font=font_medium, fill=0)

def draw_forecast(draw, x_offset, y_offset, width, height, font_small, weather_data):
    """
    Draws the 5-day weather forecast.
    """
    draw.rectangle([(x_offset, y_offset), (x_offset + width, y_offset + height)], fill=255)
    
    y_pos = y_offset + 30  # Add padding at top
    
    if weather_data and 'now' in weather_data:
        from datetime import datetime
        
        # First, show today's weather
        today_min = weather_data['now']['min']
        today_max = weather_data['now']['max']
        forecast_line = f"Today:    {today_min}°   {today_max}°"
        _, _, line_w, line_h = font_small.getbbox(forecast_line)
        draw.text((x_offset + (width - line_w) / 2, y_pos), forecast_line, font=font_small, fill=0)
        y_pos += line_h + 8
        
        # Then show next days with weekday abbreviations
        if 'forecast' in weather_data:
            for day in weather_data['forecast'][:4]:  # Show 4 more days (total 5 with today)
                # Format as 3-letter weekday
                date_obj = datetime.fromisoformat(day['date'])
                weekday = date_obj.strftime("%a")
                
                # Format: "weekday:    min   max"
                forecast_line = f"{weekday}:    {day['min']}°   {day['max']}°"
                
                _, _, line_w, line_h = font_small.getbbox(forecast_line)
                draw.text((x_offset + (width - line_w) / 2, y_pos), forecast_line, font=font_small, fill=0)
                y_pos += line_h + 8
                
                if y_pos > y_offset + height - 20:
                    break
    else:
        forecast_line = "No forecast data"
        _, _, line_w, _ = font_small.getbbox(forecast_line)
        draw.text((x_offset + (width - line_w) / 2, y_pos), forecast_line, font=font_small, fill=0)

def draw_bus_departures(draw, x_offset, width, height, font_medium, font_small):
    """
    Draws the bus departure times pane.
    """
    draw.rectangle([(x_offset, 0), (x_offset + width, height)], fill=255)
    
    title = "Bus 106 Departures \udb81\udfa0"
    _, _, w, h = font_medium.getbbox(title)
    draw.text((x_offset + (width - w) / 2, 10), title, font=font_medium, fill=0)

    # Fetch actual departure times
    departures_data = get_departures()
    departures = [(dep['time'], dep['direction']) for dep in departures_data[:3]]  # Take first 3
    
    if not departures:
        departures = [("--:--", "No data")] * 3  # Fallback if no data
    
    y_pos = 10 + h + 20
    
    # Add padding and calculate spacing to evenly distribute the times
    padding = 15
    usable_width = width - (2 * padding)
    spacing = usable_width / (len(departures) + 1)
    
    for i, (time, direction) in enumerate(departures):
        # Draw time
        _, _, time_w, time_h = font_small.getbbox(time)
        x_pos_time = x_offset + padding + spacing * (i + 1) - time_w / 2
        draw.text((x_pos_time, y_pos), time, font=font_small, fill=0)
        
        # Draw direction below time
        _, _, dir_w, _ = font_small.getbbox(direction)
        x_pos_dir = x_offset + padding + spacing * (i + 1) - dir_w / 2
        draw.text((x_pos_dir, y_pos + time_h + 5), direction, font=font_small, fill=0)

def draw_tasks(draw_bw, draw_red, x_offset, y_offset, width, height, font_medium, font_small):
    """
    Draws the tasks pane.
    """
    draw_bw.rectangle([(x_offset, y_offset), (x_offset + width, y_offset + height)], fill=255)
    
    title = "Lily's Tasks"
    _, _, w, h = font_medium.getbbox(title)
    draw_bw.text((x_offset + (width - w) / 2, y_offset + 10), title, font=font_medium, fill=0)

    tasks = get_tasks()
    y_pos = y_offset + 10 + h + 10
    max_width = width - 40  # Leave margin on right side
    
    if tasks:
        for task in tasks:
            # Parse task to find text in parentheses
            parts = re.split(r'(\([^)]*\))', task)
            
            x_pos = x_offset + 20
            line_start_x = x_offset + 20
            draw_bw.text((x_pos, y_pos), "- ", font=font_small, fill=0)
            _, _, dash_w, dash_h = font_small.getbbox("- ")
            x_pos += dash_w
            line_start_x = x_pos  # Start of actual text after dash
            
            max_line_height = dash_h
            for part in parts:
                if not part:  # Skip empty strings
                    continue
                
                # Split part into words for better wrapping
                words = part.split(' ')
                for word_idx, word in enumerate(words):
                    if word_idx > 0:
                        word = ' ' + word  # Add space back except for first word
                    
                    _, _, word_w, word_h = font_small.getbbox(word)
                    
                    # Check if word fits on current line
                    if x_pos + word_w > x_offset + max_width and x_pos > line_start_x:
                        # Move to next line
                        y_pos += max_line_height + 3
                        x_pos = line_start_x
                        max_line_height = 0
                        
                        # Remove leading space if word starts with space
                        if word.startswith(' '):
                            word = word[1:]
                            _, _, word_w, word_h = font_small.getbbox(word)
                    
                    # Draw the word
                    if part.startswith('(') and part.endswith(')'):
                        # Draw parentheses text in red
                        draw_red.text((x_pos, y_pos), word, font=font_small, fill=0)
                    else:
                        # Draw regular text in black
                        draw_bw.text((x_pos, y_pos), word, font=font_small, fill=0)
                    
                    x_pos += word_w
                    max_line_height = max(max_line_height, word_h)
            
            y_pos += max_line_height + 5
            if y_pos > y_offset + height - 20: # Don't draw off screen
                break
    else:
        draw_bw.text((x_offset + 20, y_pos), "No tasks today!", font=font_small, fill=0)


def main():
    try:
        logging.info("Home Dashboard")

        epd = epd7in5b_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        logging.info("done with Clear")

        font_large = ImageFont.truetype(os.path.join(picdir, 'MapleMonoBold.ttf'), 48)
        font_medium = ImageFont.truetype(os.path.join(picdir, 'MapleMonoBold.ttf'), 24)
        font_small = ImageFont.truetype(os.path.join(picdir, 'MapleMonoBold.ttf'), 18)

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
            forecast_pane_height = screen_height - weather_pane_height
            
            # Right pane horizontal split
            bus_pane_height = int(screen_height * 0.25)
            tasks_pane_height = screen_height - bus_pane_height

            # Fetch weather data
            weather_data = get_weather()

            # Draw Weather (top-left pane)
            draw_weather(draw_bw, 0, 0, left_pane_width, weather_pane_height, font_large, font_medium, font_small, weather_data)

            # Draw Forecast (bottom-left pane)
            draw_forecast(draw_bw, 0, weather_pane_height, left_pane_width, forecast_pane_height, font_small, weather_data)

            # Draw Bus Departures (top-right pane)
            draw_bus_departures(draw_bw, left_pane_width, right_pane_width, bus_pane_height, font_medium, font_small)

            # Draw Tasks (bottom-right pane)
            draw_tasks(draw_bw, draw_red, left_pane_width, bus_pane_height, right_pane_width, tasks_pane_height, font_medium, font_small)

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
