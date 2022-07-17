import database
from news_scrap import update_json



    
    

update_json(
database.Database().get_public_chats(), json_file='public-chats.json')
