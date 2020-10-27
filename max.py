#!/usr/bin/python3
# -*- coding:utf-8 -*-
import sys
import os
libdir = os.path.join('lib')
fontdir='/usr/share/fonts/truetype/piboto'
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in13_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

#import atexit
#import signal

import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from cal_setup import get_calendar_service

import requests
import textwrap

from datetime import datetime as dt

import random
from random import choice


import json
# base URL

CITY = "<YOUR CITY>"
API_KEY = "<https://openweathermap.org/>"



#print( custom_strftime('%B {S}, %Y', dt.now()))

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.WARNING)

try:
#logging.info("epd2in13_V2 Demo")
    epd = epd2in13_V2.EPD()
    #logging.info("init and Clear")

    # Drawing on the image
    #font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
    font15 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-Regular.ttf'), 15)
    font15_b = ImageFont.truetype(os.path.join(fontdir, 'Piboto-Bold.ttf'), 15)
    #font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font24 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-Regular.ttf'), 24)
    font33_b = ImageFont.truetype(os.path.join(fontdir, 'Piboto-Bold.ttf'), 33)

    icon_font = ImageFont.truetype("./meteocons.ttf", 40)
    ICON_MAP = { "01d": "B", "01n": "C", "02d": "H", "02n": "I", "03d": "N", "03n": "N", "04d": "Y", "04n": "Y", "09d": "Q", "09n": "Q", "10d": "R", "10n": "R", "11d": "Z", "11n": "Z", "13d": "W", "13n": "W", "50d": "J", "50n": "K" }

    #logging.info("1.Drawing on the image...")
    logging.warning("\nStarting...")

    image = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)



    time_image = Image.new('1', (epd.height, epd.width), 255)
    time_draw = ImageDraw.Draw(time_image)

    ##draw = ImageDraw.Draw(image)

    def restart():
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)

        #lines
        #draw.line([(0,43),(249,43)], fill = 0,width = 1)
        #draw.line([(0,75),(249,75)], fill = 0,width = 1)

        #draw.line([(0,75),(193,75)], fill = 0,width = 1)

        epd.displayPartBaseImage(epd.getbuffer(time_image))
        epd.display(epd.getbuffer(image))


        epd.init(epd.PART_UPDATE)
        '''
        if 'showtime' in globals():
            scheduler.pause()
            showtime()
            logging.warning("\nShowtime...")
            wait = 3
            scheduler.resume()
        else:
            logging.warning("\nFirst...")
        '''
    restart()
    gcal = []

    def google_cal():

        service = get_calendar_service()
        # Call the Calendar API
        time = datetime.datetime.utcnow()
        now = time.isoformat() + 'Z' # 'Z' indicates UTC time
        later = (time + datetime.timedelta(hours=8)).isoformat() + 'Z' # 'Z' indicates UTC time
        before = (time - datetime.timedelta(hours=1)).isoformat() + 'Z' # 'Z' indicates UTC time

        events_result = service.events().list(
            calendarId='primary', timeMin=before, timeMax=later,
            maxResults=2, singleEvents=True,
            orderBy='startTime').execute()
        events = events_result.get('items', [])

        #if not events:
        #    print('No upcoming events found.')
        global gcal
        gcal.clear()
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = datetime.datetime.strptime(start[0:19],"%Y-%m-%dT%H:%M:%S").strftime("%H:%M")
            #print(start, event['summary'])
            #print(start, event['summary'])
            gcals = start + ' ' + event['summary']
            gcal.append(gcals)

    google_cal()
    temperature = ""
    icon = ""
    place = ""
    description = ""
    def weather():
        BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
        URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY + "&units=metric"

        global temperature
        global icon
        global place
        global description
        # HTTP request
        response = requests.get(URL)
        # checking the status code of the request
        ##print(response)
        if response.status_code == 200:
           # getting data in the json format
           data = response.json()
           # getting the main dict block
           main = data['main']
           # getting temperature
           temperature = format(main['temp'], '5.2f')
           '''
           temperature = temperature * -1
           if temperature < 0:
               tmv = 5
           else:
               tmv = 0
           '''
           tmv = 0
           weath = data['weather']
           #self._weather_icon = ICON_MAP[weather["weather"][0]["icon"]]
           icon = ICON_MAP[weath[0]['icon']]
           description = weath[0]['description']
           place = data['name']
           # getting the humidity
           ##humidity = main['humidity']
           # getting the pressure
           ##pressure = main['pressure']
           # weather report
           ##report = data['weather']
           ##print(URL)
           ##print(f"{CITY:-^30}")
           ##print(f"Temperature: {temperature}")
           ##print(f"Humidity: {humidity}")
           ##print(f"Pressure: {pressure}")
           ##print(f"Weather Report: {report[0]['description']}")
           feels_like = main['feels_like']
           humidity = main['humidity']
           pressure = round(main['pressure'] * 0.75006156130264, 1)
           #winds = wind['speed']
           #windd = wind['deg']
           temp_min = format(main['temp_min'], '5.2f')
           temp_max = format(main['temp_max'], '5.2f')
           #sunrise = sys['sunrise']
           #sunset = (datetime.now() - datetime.utcnow() + datetime.utcfromtimestamp(sys['sunset'])).strftime('%H:%M')
           #print(feels_like,humidity,pressure)
           ##ss1 = '--------\n' + 'Weather:' + '\n' + str(CITY) + '\n' + 'Current: ' + str(temperature) + '°C' + '\n' + 'Feels like: ' + str(feels_like) + '°C' + '\n' + 'Humidity: ' + str(humidity) + ' %' + '\n' + 'Pressure: ' + str(pressure) + ' mmHg' + '\n' + 'Wind: ' + str(winds) + 'm/s ' + 'direction: ' + str(windd) + '°' + '\n' + 'sunrise at ' + str(sunrise) + ' ,sunset at ' + str(sunset) +  '\n' + 'You may see some ' + str(description) + ' in ' + str(CITY) + '\n--------'
           #ss1 = '--------\n' + 'Weather:' + '\n' + str(CITY) + '\n' + 'Current: ' + str(temperature) + '°C' + '\n' + ', from ' + str(temp_min) + '°C' + ' to ' + str(temp_max) + '°C' + '\n' + 'Feels like: ' + str(feels_like) + '°C' + '\n' + 'Humidity: ' + str(humidity) + ' %' + '\n' + 'Pressure: ' + str(pressure) + ' mmHg' + '\n' + 'Wind: ' + str(winds) + 'm/s ' + 'direction: ' + str(windd) + '°'  +  '\n' + 'You may see some ' + str(description) + ' in ' + str(CITY) + '\n--------'
           ss1 = '--------\n' + 'Weather:' + '\n' + str(CITY) + '\n' + 'Current: ' + str(temperature) + '°C' + '\n' + 'From ' + str(temp_min) + '°C' + ' to ' + str(temp_max) + '°C' + ', feels like: ' + str(feels_like) + '°C' + '\n' + 'Humidity: ' + str(humidity) + ' %' + '\n' + 'Pressure: ' + str(pressure) + ' mmHg' + '\n' + 'You may see some ' + str(description) + ' in ' + str(CITY) + '\n--------'
           cmd = "echo "+ '"' + ss1 + '"' + "> /run/user/1000/weather"
           os.system(cmd)

           time_draw.rectangle((133-tmv, 59, 180, 75), fill = 255)
           time_draw.text((133-tmv, 56), str(temperature) + '°C', font = font15_b, fill = 0)

           time_draw.rectangle((208, 35, 248, 78), fill = 255)
           time_draw.text((208, 35), icon, font = icon_font, fill = 0)
        else:
           # showing the error message
           print("Error in the HTTP request")

    weather()
    def string_divide(string, div):
       l = []
       wrapper = textwrap.TextWrapper(width=div)
       #word_list1 = wrapper.wrap(text=string)
       #word_list = wrapper.fill(text=word_list1)
       word_list = wrapper.wrap(text=string)

       for element in word_list:
           l.append(element)
       ex = '\n'.join(l)
       #return l
       return ex


    '''
    def string_divide_t(string, div):
           l = []
           for i in range(0, len(string), div):
               l.append(string[i:i+div])
           return l
    '''
    #llen = 0
    lang = ""
    d_quote = ""
    quote_div = ""
    def dquote():

        global quote_div
        global d_quote

        response = requests.get("http://www.quotedb.com/quote/quote.php?action=random_quote").text

        d_quote = response.split("'")[1].replace("<br>", "") + '  ' + response.split("'")[3].split(">")[2].split("<")[0]


    def fquote():
        global d_quote
        global lang
        lang = choice(['en', 'ru'])
        response = requests.get("http://api.forismatic.com/api/1.0/?method=getQuote&lang="+ lang + "&format=json")
        if response.status_code == 200:
           responseJson = json.loads(response.text)
           author = responseJson['quoteAuthor']
           quote = responseJson['quoteText']
           d_quote = quote + '  ' + author
        else:
           dquote()
           logging.warning("\nCheck api.forismatic.com...")


    def quoting():
        global quote_div
        font11 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-ThinItalic.ttf'), 11)
        random.choice([dquote,fquote])()
        #dquote()


        lenq = 49
        if lang == 'ru':
            lenq = 45
        count = 0
        max_guesses_allowed = 3 #pick your max here
        while len(d_quote)>lenq*3 or len(d_quote)<5 or count < max_guesses_allowed:
            count += 1
            random.choice([dquote,fquote])()
        if len(d_quote)<lenq*2:
            if len(d_quote)>75:
                lenq = lenq - 6
                font11 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-ThinItalic.ttf'), 13)
            else:
                lenq = lenq - 10
                font11 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-ThinItalic.ttf'), 15)
        #resize
        '''
        if len(d_quote)/3>lenq:
            lenq = round(len(d_quote)/3)
        if len(d_quote)/2.2<lenq:
            lenq = round(len(d_quote)/2)
        '''
        #resize

        #resize
        '''
        def resizing():
            font = os.path.join(fontdir, 'Piboto-ThinItalic.ttf')
            text = quote_div
            size = 11
            counter = 0

            def get_total_area(width, height):
                return width * height
            def get_font(name, size):
                return ImageFont.truetype(font, size)

            def fit(width, height, font, size, text):
                font = get_font(font, size)
                text_w, text_h = font.getsize(text)
                text_area = get_total_area(text_w, text_h)
                total_area = get_total_area(width, height)
                if total_area>text_area:
                    return True
                else:
                    scale = total_area/text_area
                    size = int(round(size*scale))
                    return size
            while True:
                ans = fit(249, 128, font, size, text)
                if ans == True:
                    break
                else:
                    size = ans
                    size -=1

            global font11
            font11 = ImageFont.truetype(os.path.join(fontdir, 'Piboto-ThinItalic.ttf'), size)
        resizing()
        '''
        #resize

        quote_div = string_divide(d_quote ,lenq)
        #quote_div = d_quote

        logging.warning('\nQuote:\n' + d_quote)
        ss2 = '--------\n' + str(d_quote) + '\n--------'
        cmd2="echo " + '"' + ss2.replace('"' ,"'") + '"' + "> /run/user/1000/quote"
        os.system(cmd2.replace("`" ,"'"))

        #if 'quote_div' in globals():
        time_draw.rectangle((2, 76, 249, 121), fill = 255)
        time_draw.text((2, 76), quote_div, font = font11, fill = 0)
    quoting()

    bmp = ""
    imageview_m = 10080
    def imageview():
        ##imageview_image = Image.new('1', (249, 39), 255)
        ##imageview_draw = ImageDraw.Draw(imageview_image)
        url1 = 'https://www.gimplearn.net/fun.php?q='
        url2 = description
        #url2 = description + ' in ' + place
        #url2 = 'city%20panorama'
        os.system("./curlconv {}".format(url1 + ' ' + url2.replace(' ' ,'%20') + ' ' + '39'))
        #logging.warning((url1 + ' ' + url2.replace(' ' ,'%20') + ' ' + '39'))
        global bmp
        bmp = Image.open('/run/user/1000/output.bmp')
        image.paste(bmp, (0,0))

        global imageview_m
        if 0 < len(gcal):
            imageview_m = 10080
            time_draw.rectangle((0, 0, 249, 20), fill = 255)
            time_draw.text((0, 0), gcal[0], font = font15_b, fill = 0)
        if 1 < len(gcal):
            time_draw.rectangle((0, 20, 249, 40), fill = 255)
            time_draw.text((0, 20), gcal[1], font = font15, fill = 0)
        else:
            imageview_m = 30
            time_draw.rectangle((0, 0, 248, 39), fill = 255)
            time_image.paste(bmp, (0,0))
        ##epd.displayPartial(epd.getbuffer(time_image))
    imageview()

    def suffix(d):
        return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

    def custom_strftime(format, t):
        return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

    def showtime():

        #gcal = ["14:00 Test 1", "15:00 Test 2"]


        #time_draw.rectangle((0, 20, 220, 105), fill = 255)
        #time_draw.text((0, 20), gcal, font = font24, fill = 0)

        time_draw.rectangle((0, 43, 86, 75), fill = 255)
        time_draw.text((0, 36), custom_strftime('%H:%M', dt.now()), font = font33_b, fill = 0)

        time_draw.rectangle((101, 43, 180, 59), fill = 255)
        time_draw.text((101, 42), custom_strftime('%B {S}', dt.now()), font = font15_b, fill = 0)
        time_draw.rectangle((101, 59, 115, 75), fill = 255)
        time_draw.text((101, 56), custom_strftime('%a', dt.now()), font = font15_b, fill = 0)

        epd.displayPartial(epd.getbuffer(time_image))

    showtime()
    scheduler = BlockingScheduler()
    scheduler.add_job(showtime, 'interval', minutes=1, start_date=time.strftime('%Y-%m-%d %H:%M') + ':00')
    #scheduler.add_job(showtime, 'interval', seconds=10)
    scheduler.add_job(google_cal, 'interval', minutes=5)
    scheduler.add_job(quoting, 'interval', minutes=10)
    scheduler.add_job(weather, 'interval', minutes=30)

    scheduler.add_job(imageview, 'interval', minutes=imageview_m)
    #job_defaults = {'coalesce': False,'max_instances': 4}
    #scheduler.add_job(restart, 'interval', seconds=30)
    scheduler.start()


except KeyboardInterrupt:
    logging.warning("ctrl + c:")
    time_image.save('current.png')
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    epd2in13_V2.epdconfig.module_exit()
    exit(0)
except Exception:
    pass
