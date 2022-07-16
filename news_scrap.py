#!/usr/bin/env python3

import logging
import sys
from time import sleep
from telegram import InputMediaPhoto, InputMediaVideo
from telegram.constants import ParseMode

import twint
from datetime import datetime, timedelta
from globals import BOT, DATE_FORMATE, PUBLIC_CHATS, BaseModel, get_video_url, orjson
import asyncio

from utils import normalize_tweet
# Configuratoin of the logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Logger
log = logging.getLogger(__name__)




        
class Channel(BaseModel):
    
    username : str
    since : datetime    
    
    def sinceStr(self):
        return self.since.strftime(DATE_FORMATE)
    
        
async def publish(tweet, photos_urls, video_url):
    tw = normalize_tweet(tweet.tweet)
    num_photos = len(photos_urls)
    media_group = []
    message = (
        f'<strong>{tweet.name}</strong>\n'
        f'{tw}'
    )
    try:
        if num_photos == 0 and  video_url is None:
            for i in PUBLIC_CHATS:
                await BOT.send_message(chat_id=i.chat_id, text=message, parse_mode=ParseMode.HTML)
        else:
            caption_embeded = False
            if video_url is not None:
                caption_embeded = True
                media_group.append(InputMediaVideo(video_url, caption= message , parse_mode = ParseMode.HTML))
            if num_photos > 0:
                for i in range(num_photos):
                    media_group.append(InputMediaPhoto(photos_urls[i], caption= message if not caption_embeded and i ==0 else '' , parse_mode = ParseMode.HTML if not caption_embeded and i ==0  else ''))

            for i in PUBLIC_CHATS:
                await BOT.send_media_group(chat_id=i.chat_id, media= media_group)
        
    except Exception as exp:
        log.error(f'Error: An exception occured while publishing posts.\n Exception : {exp}\n Traceback : {exp.__context__}' )
        

  
def read_channels(json_file : str = "channels.json") -> list[Channel]:
    """Used to read json file that holds all channels data to get tweets"""
    file = open(json_file, "r")
    channels = list(map(Channel.parse_obj ,[i for i in orjson.loads(file.read())]))
    file.close()
    return channels

def update_channels(channels : list[Channel], json_file : str = "channels.json",) -> None:
    """Update since field in the json file for each channel"""
    channels_len = len(channels)
    file = open(json_file, 'w')
    # Move the fd to th ebegining of the file
    file.seek(0)
    #Delete all data
    file.truncate()
    file.write(r'[')
    for index in range(channels_len):
        file.write(channels[index].json())
        # to skip writting of ',' for the last channel
        if index == (channels_len - 1):
            continue
        file.write(r',')
    file.write(r']')
    
          
def main():
    log.info("Reading channels data from json.")
    conf = twint.Config()
    loop = asyncio.new_event_loop()
    channels = read_channels()

    while True:
        try:
            for i in range(len(channels)):
                tweets = []
                conf.Username = channels[i].username
                conf.Since = channels[i].sinceStr()
                conf.Store_object = True
                conf.Store_object_tweets_list = tweets
                conf.Hide_output = True
                twint.run.Search(conf)
                for index in range(len(tweets)):
                    # Parse str to datetime. for compersion. remove +03 to keep with our date_format
                    date = datetime.strptime(tweets[index].datetime.replace(" +03", ""), DATE_FORMATE)   
                    if channels[i].since < date:
                        channels[i].since = date +timedelta(minutes=2)
                    
                    if tweets[index].video:
                        video_url = get_video_url(tweets[index].link)
                    else :
                        video_url = None
                    
                    loop.run_until_complete(publish(tweet=tweets[index],photos_urls= tweets[index].photos, video_url=video_url))

            #1 min until next exection      
            log.info("Sleeping for 1 min.")      
            sleep(60)
            
                
        except KeyboardInterrupt:                        
            log.info("Updating channels in json file.")     
            update_channels(channels)
            
            log.info("\n[Exiting] Keyboard interupt.")
            sys.exit(1)
        except Exception as exp:
            log.info(f'An Exception occurend {exp.with_traceback}. Cause : {exp.__cause__}\n Updating Channels and retrying from main().')
            update_channels(channels)
            main()


if __name__ == '__main__':
    main()