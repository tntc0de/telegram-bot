from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from logging import getLogger

import orjson



class DBSetup:
    DB_URL =  "postgresql://hadus:toor@localhost:5432/newsbot_db"
    BASE = declarative_base()
    ENGINE = create_engine(DB_URL)
    
    @classmethod
    def create_all(cls):
        cls.BASE.metadata.create_all(cls.ENGINE)

class DBPublicChat(DBSetup.BASE):
    __tablename__ = 'public_chats'
    
    chat_id = Column(String, primary_key=True)
    type = Column(Integer)
    username  = Column(String)
    title = Column(String)
    
    
class DBAdmin(DBSetup.BASE):
    __tablename__ = 'admins'
    
    chat_id = Column(Integer, primary_key=True)
    username  = Column(String)
    name = Column(String)
    
    
class DBPrivateCHat(DBSetup.BASE):
    __tablename__ = 'private_chats'
    
    chat_id = Column(Integer, primary_key=True)
    username  = Column(String)
    name = Column(String)
    
    

PublicChat = sqlalchemy_to_pydantic(DBPublicChat)
Admin = sqlalchemy_to_pydantic(DBAdmin)
PrivateChat = sqlalchemy_to_pydantic(DBPrivateCHat)

DBSetup.create_all()

def read_chats(json_file : str = "public-chats.json") -> list[PublicChat]:
    """Used to read json file that holds all channels data to get tweets"""
    file = open(json_file, "r")
    public_chats = list(map(PublicChat.parse_obj ,[i for i in orjson.loads(file.read())]))
    file.close()
    return public_chats

class Database:
    def __init__(self, base = DBSetup.BASE , engine= DBSetup.ENGINE):        
        self._session = scoped_session(sessionmaker(bind= engine))
        self._db  : Session = self._session()
        
        _public_chats = read_chats()
        for i in _public_chats:
            _chat = self.get_public_chat(i.chat_id)
            if _chat is None:
                self.add_public_chats(_chat)  
        self.logger = getLogger(__name__)
        
    def get_admins(self):
        _admins = []
        for i in self._db.query(DBAdmin).all():
            _admins.append(Admin.from_orm(i))

        return _admins
    
    def add_admin(self,admin : Admin):
        try:
            _admin = DBAdmin(chat_id=admin.chat_id, username=admin.username, name=admin.name)
            
            self._db.add(_admin)
        except Exception as excp:  # pylint: disable=W0703
            self._db.close()
            self.logger.error(
                "Failed to save data in the database.\nLogging exception: ",
                exc_info=excp,
            )
            
        
    def delete_admin(self,chat_id):
        try:
            
            self._db.query(DBAdmin).filter(DBAdmin.chat_id==chat_id).delete()
            
        except Exception as excp:  # pylint: disable=W0703
            self._db.close()
            self.logger.error(
                "Failed to save data in the database.\nLogging exception: ",
                exc_info=excp,
            )
        
    def get_public_chats(self):
        _public_chats = []
        
        for i in self._db.query(DBPublicChat).all():
            _public_chats.append(PublicChat.from_orm(i))
            
        return _public_chats
    
    def get_public_chat(self, chat_id):
        return self._db.query(DBPublicChat).get(chat_id)
            
   
    def add_public_chats(self, public_chat : PublicChat):
        try:
            _public_chat = DBPublicChat(chat_id=public_chat.chat_id, username=public_chat.username, title=public_chat.title, type=public_chat.type)
            
            self._db.add(_public_chat)
        except Exception as excp:  # pylint: disable=W0703
            self._db.close()
            self.logger.error(
                "Failed to save data in the database.\nLogging exception: ",
                exc_info=excp,
            )
    
        
    def get_private_chats(self):
        _private_chats = []
        
        for i in self._db.query(DBPrivateCHat).all():
            _private_chats.append(i)
            
        return _private_chats
    
    def add_private_chat(self, private_chat : PrivateChat):
        try:
            _private_chat = DBPrivateCHat(chat_id=private_chat.chat_id, username=private_chat.username, title=private_chat.title, type=private_chat.type)
            
            self._db.add(_private_chat)
        except Exception as excp:  # pylint: disable=W0703
            self._db.close()
            self.logger.error(
                "Failed to save data in the database.\nLogging exception: ",
                exc_info=excp,
            )
        
    def commit(self):
        self._db.commit()
        

        

        


        



db = Database()



