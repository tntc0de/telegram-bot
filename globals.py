from datetime import datetime
import orjson
from pydantic import BaseModel as PyBaseModel
import subprocess
from telegram import Bot
from database import db

DATE_FORMATE = "%Y-%m-%d %H:%M:%S"
# Get all channels and groups from database
PUBLIC_CHATS = db.get_public_chats()

# Initiliaze Bot config
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

