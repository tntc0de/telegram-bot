

import re

channels_hashes = set(['#الحدث', "#الحدث_اليمن"])
def remove_urls(text : str):
    return re.sub(r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])', '', text, flags=re.MULTILINE)


def remove_channel_hash(text):
    for i in channels_hashes :
        text = re.sub(i, "", text)
        
    return text


def normalize_tweet(text):
    return remove_urls(remove_channel_hash(text))

