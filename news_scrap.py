#!/usr/bin/env python3

import sys
from time import sleep
from telegram import InputMediaPhoto, InputMediaVideo, Bot
from telegram.constants import ParseMode
from pydantic import BaseModel as PyBaseModel
import twint
from datetime import datetime, timedelta
import asyncio
import subprocess
import orjson
from utils import normalize_tweet



DATE_FORMATE = "%Y-%m-%d %H:%M:%S"

BOT = Bot('5594405619:AAGIZI-hF0IChdvM_GAof-TQepniP0BvCDA')

def date_to_str(obj):
    """Convert datetime obj to specifice str formate"""
    if isinstance(obj, datetime):
        return obj.strftime(DATE_FORMATE)
    raise TypeError
    
    
def orjson_dumps(v, *, default=None):
    """
    Change the default deserilization of orjson.
    Instead of default deserilization of datetime obj to str with utc. We used date_to_str function.
    """
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v,default=date_to_str, option=orjson.OPT_PASSTHROUGH_DATETIME,).decode()

class BaseModel(PyBaseModel):
    """Class define shared config"""
    class Config:
        #Strip any whitrspace in str
        anystr_strip_whitespace = True
        #Use custome functoin to load json str instead of json.loads
        json_loads = orjson.loads 
        json_dumps = orjson_dumps
        
        

def get_video_url(tweet_link : str):
    process = subprocess.Popen(['youtube-dl', '--get-url', tweet_link],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if len(stdout.decode('utf-8')) <=1:
        return None
    return stdout.decode('utf-8')

        
class Channel(BaseModel):
    
    username : str
    since : datetime    
    
    def sinceStr(self):
        return self.since.strftime(DATE_FORMATE)
    
class PublicChat(BaseModel):
    
    chat_id : str
    title : str    
    username: str
    type : int
    


def read_chats(json_file : str = "public-chats.json") -> list[PublicChat]:
    """Used to read json file that holds all channels data to get tweets"""
    file = open(json_file, "r")
    public_chats = list(map(PublicChat.parse_obj ,[i for i in orjson.loads(file.read())]))
    file.close()
    return public_chats

PUBLIC_CHATS = read_chats()
    
        
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
        pass
        

  
def read_channels(json_file : str = "channels.json") -> list[Channel]:
    """Used to read json file that holds all channels data to get tweets"""
    file = open(json_file, "r")
    channels = list(map(Channel.parse_obj ,[i for i in orjson.loads(file.read())]))
    file.close()
    return channels


def update_json(classes_list : list, json_file : str = "channels.json",) -> None:
    """Update since field in the json file for each channel"""
    channels_len = len(classes_list)
    file = open(json_file, 'w')
    # Move the fd to th ebegining of the file
    file.seek(0)
    #Delete all data
    file.truncate()
    file.write(r'[')
    for index in range(channels_len):
        file.write(classes_list[index].json())
        # to skip writting of ',' for the last channel
        if index == (channels_len - 1):
            continue
        file.write(r',')
    file.write(r']')
    
          
def main():
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
            sleep(60)
            
                
        except KeyboardInterrupt:                        
            update_json(channels)
            
            sys.exit(1)
        except Exception as exp:
            update_json(channels)
            main()


if __name__ == '__main__':
    main()