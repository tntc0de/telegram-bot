
import asyncio
import os
from database import db, Admin

from functools import wraps

from telegram.constants import ParseMode
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, filters, ContextTypes , ConversationHandler, MessageHandler




TOKEN = "5594405619:AAGIZI-hF0IChdvM_GAof-TQepniP0BvCDA"
PORT = int(os.environ.get('PORT', '8443'))

BOT = Bot(TOKEN)

ADMINS = db.get_admins()
PUBLIC_CHATS = db.get_public_chats()

AUTHENTICATE, BASM_ALLAH = range(2) 
def super_restriction(func):
    @wraps(func)
    async def wrapped(update : Update, context, *args, **kwargs):
        user = Admin(chat_id = update.effective_user.id,username=update.effective_user.username, name=update.effective_user.full_name)
        exists = [i for i in ADMINS if i.chat_id == user.chat_id]
        if len(exists)==0 or exists == None:
            return
        return await func(update, context, *args, **kwargs)
    return wrapped


@super_restriction
async def role(update : Update, context:ContextTypes.DEFAULT_TYPE):    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Welcome {update.effective_chat.full_name} : You\'r admin.')
    



@super_restriction
async def tokal(update : Update , context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "  ادخل رمز التاكيد لمتابعة العملية"
    )
    
    return AUTHENTICATE

async def authenticate(update : Update, context : ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    if code == '12345':
        await update.message.reply_text(
            'تم التخقق من الرمز بنجاح\n'
            ' توكلوا على الله الواحد ثم ارسلوا الملف مع الوصف الخاص به\n'
            " في حالة الغاء العملية قوم بارسال الامر\n"
            "<code> /end </code>\n",
            parse_mode=ParseMode.HTML
        )
        return BASM_ALLAH
    else:
        await update.message.reply_text(
            'رمز التحقق غير صحيح سوف يتم انهاء العملية'
        )
        return ConversationHandler.END
        
async def basm_allah(update : Update, context : ContextTypes.DEFAULT_TYPE):
    if update.message.document is not None:
        if len(update.message.caption) == 0:
            await update.message.reply_text(quote=True, text='الرجاء اضافة وصف للمرفق لجعله اكثر أقناعا للاشخاص ليقوموا بتنزيل المرفق بأذن الله.')
            return ConversationHandler.WAITING
        for i in PUBLIC_CHATS:
            m = await context.bot.send_document(chat_id=i.chat_id, document=update.message.document, caption=update.message.caption)
            await m.pin()
        
        await update.message.reply_text('الحمدلله تم ارسال المرفق لكل القنوات و المجموعات المسجله.\nالله يسدد\n')
        return ConversationHandler.END
    elif len(update.message.photo) != 0:
        if len(update.message.caption) == 0:
            await update.message.reply_text(quote=True, text='الرجاء اضافة وصف لصورة  او رابط الى موقع ملغم')
            return ConversationHandler.WAITING
        for i in PUBLIC_CHATS:
            m = await context.bot.send_photo(chat_id=i.chat_id, photo=update.message.photo[-1], caption=update.message.caption)
            await m.pin()
        
        await update.message.reply_text('الحمدلله تم ارسال الصورة لكل القنوات و المجموعات المسجله.\nالله يسدد\n')
        return ConversationHandler.END
       
    else :
        return ConversationHandler.END

    
                
                
async def end(update : Update, context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'تم انهاء العملية'
    )
    
    return ConversationHandler.END

def test():
    application = ApplicationBuilder().bot(BOT).build()

    role_handlers = CommandHandler('role', role, filters.ChatType.PRIVATE | filters.ChatType.GROUPS)
    cove_handler = ConversationHandler(
        entry_points=[CommandHandler('tokal', tokal)],
        states={
            AUTHENTICATE : [
                MessageHandler(filters.TEXT, authenticate)
            ],
            BASM_ALLAH : [
                MessageHandler((filters.PHOTO | filters.Document.APK) & filters.ChatType.PRIVATE, basm_allah )
                
            ]
        },
        fallbacks=[CommandHandler('end', end)]
    )
    application.add_handler(role_handlers)
    application.add_handler(cove_handler)
    
    


    # add handlers
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url="https://telegram-bot-tweet-scrapper.herokuapp.com/" + TOKEN
    )
    

if __name__ == '__main__':
    test()
