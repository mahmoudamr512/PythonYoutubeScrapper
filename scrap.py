import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pytube import Channel
import random
import re
import json

class Scrap:

    __proxies = [
        '64.227.14.149:80',
        '50.218.57.68:80',
        '50.218.57.69:80',
        '50.218.57.70:80',
        '50.218.57.65:80',
        '50.217.22.107:80',
        '50.217.22.108:80',
        '65.51.178.93:3128',
        '50.228.83.226:80',
        '50.228.141.98:80',
        '50.220.21.202:80',
        '50.217.153.72:80',
        '50.217.153.79:80',
        '50.228.193.10:80',
        '50.216.216.64:80',
        '50.216.216.66:80',
        '50.235.240.86:80',
        '50.228.141.101:80',
        '50.204.233.30:80',
        '50.206.111.89:80',
        '20.47.108.204:8888',
        '50.206.25.110:80',
        '50.206.25.104:80',
        '50.206.25.106:80',
        '50.206.25.109:80',
        '50.206.25.111:80',
        '50.206.25.105:80',
        '50.206.25.107:80',
        '50.206.25.108:80',
        '50.237.89.170:80',
    ]
    __headers = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12.3; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15'
    ]

    __DRIVE_PATH = 'chromedriver'

    __data = {
        "Video ID": "",
        "Title": "",
        "Views": "",
        "Duration": "",
        "Publish Date": "",
        "Channel Name": "",
        "Channel Subs": "",
        "Views / Day": "",
        "Views / Hours": "",
    }


    __videoHTML = None

    def get_chanel_videos(self):
        c = Channel(self.video_url)
        return c.video_urls

    def __get_chanel_subs(self):
        data = re.search(r"var ytInitialData = ({.*?});", self.__videoHTML.prettify()).group(1)
        data_json = json.loads(data)
        videoPrimaryInfoRenderer = \
        data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
            'videoPrimaryInfoRenderer']
        videoSecondaryInfoRenderer = \
        data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1][
            'videoSecondaryInfoRenderer']
        channel_subscribers = \
        videoSecondaryInfoRenderer['owner']['videoOwnerRenderer']['subscriberCountText']['accessibility'][
            'accessibilityData']['label']
        return self.format_subs(channel_subscribers)

    def format_subs(self, subs):
        try:
            subs = subs.split(' ')[0]
            if subs[-1] == 'K':
                subs = int(float(subs[:-1])*1000)
            else:
                subs = int(float(subs[:-1])*1000000)
            self.__data["Channel Subs"] = subs
        except:
            self.__data["Channel Subs"] = None

    # Beautiful Soup Scrap the video page
    def __video_html(self):
        done = False
        while not done:
            try:
                index = random.randint(0, len(self.__proxies) - 1)
                self.__proxies = {'http': self.__proxies[index], 'https:': self.__proxies[index]}
                self.__headers = {'User-Agent': self.__headers[random.randint(0, len(self.__headers) - 1)],
                                  'Accept-Language': 'en-US'}

                # getting the request from url
                r = requests.get(self.video_url, headers=self.__headers, proxies=self.__proxies, timeout=5)

                # converting the text to BS4 Object for scraping
                self.__videoHTML = BeautifulSoup(r.text, "lxml")
                done = True
            except Exception as e:
                print(self.__videoHTML)
                raise


    # Format Time Duration as needed.
    def __format_duration(self, duration):
        h, m, s = re.findall(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)[0]
        total_time = ""
        if h == "":
            h = "00"
        else:
            h = h.replace("H", "")
        if m == "":
            m = "00"
        else:
            m = m.replace("M", "")

        if s == "":
            s = "00"
        else:
            s = s.replace("S", "")

        total_time = "{}H:{}M:{}S".format(h, m, s)
        return total_time

    # Format the Date as needed.
    def __format_date(self, date):
        pd = datetime.fromisoformat(date)
        self.__data["Publish Date"] = pd.strftime('%d %b, %Y')
        now = datetime.now().timestamp()
        pd = pd.timestamp()
        difference = (now - pd)
        hours = (difference/(3600)).__ceil__()
        days = (difference /(86400)).__ceil__()
        self.__data["Views / Hours"] = (int(self.__data["Views"])/hours).__round__()
        self.__data["Views / Day"] = (int(self.__data["Views"])/days).__round__()

    # Get all the required info from video page.
    def __scrape_video_info(self):

        # Getting VideoID
        try:
            self.__data["Video ID"] = self.__videoHTML.select_one('meta[itemprop="videoId"][content]')['content']
            # Getting YouTube Video Title
            self.__data["Title"] = self.__videoHTML.select_one('meta[itemprop="name"][content]')['content']

            # Getting YouTube Video Views
            self.__data["Views"] = "{}".format(
                int(self.__videoHTML.select_one('meta[itemprop="interactionCount"][content]')['content']))

            # Getting Video Duration
            duration = self.__videoHTML.select_one('meta[itemprop="duration"][content]')['content']
            self.__data["Duration"] = self.__format_duration(duration)

            # Getting Video Publish Date
            date_published = self.__videoHTML.select_one('meta[itemprop="datePublished"][content]')['content']
            self.__format_date(date_published)

            # Getting Channel ID
            self.channelID = self.__videoHTML.select_one('meta[itemprop="channelId"][content]')['content']

            # Getting Channel Name
            self.__data["Channel Name"] = self.__videoHTML.select_one('link[itemprop="name"][content]')['content']
            # Getting channel Subs
            try:
                self.__get_chanel_subs()
            except:
                self.__data["Channel Subs"] = None
        except:
            print("")
            print("Video Removed By Uploader")
            print(self.video_url)
            return ""





    def run_video_scrapper(self):
        self.__video_html()
        self.__scrape_video_info()
        return self.__data



    def __init__(self, *args):
        self.video_url = args[0]
