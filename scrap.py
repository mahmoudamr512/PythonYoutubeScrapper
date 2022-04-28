import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from pytube import Channel
import random


class Scrap:
    __headers = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12.3; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15'
    ]

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

    # Beautiful Soup Scrap the video page
    def __video_html(self):

        # getting the request from url
        r = requests.get(self.video_url, headers=self.__headers)

        # converting the text to BS4 Object for scraping
        self.__videoHTML = BeautifulSoup(r.text, "lxml")

    # Called to Get Subscribers Count From SocialBlade
    def __scrape_video_channel_socialblade(self, channel_id):
        r = requests.get(f'https://socialblade.com/youtube/channel/{channel_id}', headers=self.__headers)
        channel = BeautifulSoup(r.text, "lxml")
        subs = channel.find("span", {"id": "youtube-stats-header-subs"})
        if subs != None:
            subs = subs.text
        return subs

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
        self.__video_html()
        # Getting VideoID
        self.__data["Video ID"] = self.__videoHTML.select_one('meta[itemprop="videoId"][content]')['content']

        # Getting YouTube Video Title
        self.__data["Title"] = self.__videoHTML.select_one('meta[itemprop="name"][content]')['content']

        # Getting YouTube Video Views
        self.__data["Views"] = "{}".format(int(self.__videoHTML.select_one('meta[itemprop="interactionCount"][content]')['content']))

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

        # Getting Sub Count From Social Blade
        self.__data["Channel Subs"] = self.__scrape_video_channel_socialblade(self.channelID)

    def run_video_scrapper(self ):
        try:
            self.__scrape_video_info()
            return self.__data
        except:
            print("FAILED")

    def __init__(self, *args):
        self.__headers = {'User-Agent': self.__headers[random.randint(0,len(self.__headers)-1)]}
        self.video_url = args[0]
