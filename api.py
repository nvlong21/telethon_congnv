import base64
import os
import hypercorn.asyncio
from quart import Quart, jsonify, render_template_string, request
from quart_cors import cors
import asyncio
import logging
from telethon.tl.patched import MessageService
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon import TelegramClient
import pymongo
import uuid

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
mycol = mydb["customers"]
forward_col = mydb["forwards"] 
def get_env(name, message):
    if name in os.environ:
        return os.environ[name]
    return input(message)
# class TeleCl:
#     def __init__(self):
#         self.client = None

# tele_cl = TeleCl()
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
    <head>
        <meta charset='UTF-8'>
        <title>Telethon + Quart</title>
    </head>
    <body>{{ content | safe }}</body>
</html>
'''

PHONE_FORM = '''
<form action='/' method='post'>
    Phone (international format): <input name='phone' type='text' placeholder='+34600000000'>
    <input type='submit'>
</form>
'''

CODE_FORM = '''
<form action='/' method='post'>
    Telegram code: <input name='code' type='text' placeholder='70707'>
    <input type='submit'>
</form>
'''

PASSWORD_FORM = '''
<form action='/' method='post'>
    Telegram password: <input name='password' type='text' placeholder='your password'>
    <input type='submit'>
</form>
'''

# Session name, API ID and hash to use; loaded from environmental variables
# SESSION = os.environ.get('TG_SESSION', 'quart')
# API_ID = int(get_env('TG_API_ID', 'Enter your API ID: '))
# API_HASH = get_env('TG_API_HASH', 'Enter your API hash: ')

API_ID = "14225107" #os.getenv('api_id')
API_HASH = "bc6b2686eea4dc38f72181dd8d279dbf" #os.getenv('api_hash')
SESSION =  str(uuid.uuid4().hex)#os.getenv('STRING_SESSION')

# Render things nicely (global setting)
# Message.set_default_parse_mode('html')

client = None
phone = None
list_client = []
# Quart app
app = Quart(__name__)
app.secret_key = 'CHANGE THIS TO SOMETHING SECRET'
app = cors(app, allow_origin="*")

def process_phone(phone):
    return phone.replace(" ", "").replace("(", "").replace(")", "")

# Helper method to format messages nicely
async def format_message(message):
    if message.photo:
        content = '<img src="data:image/png;base64,{}" alt="{}" />'.format(
            base64.b64encode(await message.download_media(bytes)).decode(),
            message.raw_text
        )
    else:
        # The Message parse_mode is 'html', so bold etc. will work!
        content = (message.text or '(action message)').replace('\n', '<br>')

    return '<p><strong>{}</strong>: {}<sub>{}</sub></p>'.format(
        utils.get_display_name(message.sender),
        content,
        message.date
    )


# # Connect the client before we start serving with Quart
@app.before_serving
async def startup():
    global list_client
    for x in mycol.find({"status": 1}):
        print(x)
        session = x["name"]
        cl = TelegramClient(session, API_ID, API_HASH)
        await cl.connect()
        if await cl.is_user_authorized():
            list_client.append(cl)
        else:
            myquery = { "name":  session}
            newvalues = { "$set": { "status": 0 } }
            x = mycol.update_many(myquery, newvalues)


# # After we're done serving (near shutdown), clean up the client
# @app.after_serving
# async def cleanup():
#     await client.disconnect()

@app.route('/session', methods=['GET', 'POST'])
async def all_session():
    list_session = []
    response_object = {'status': 'success'}
    for x in mycol.find({}):
        list_session.append({
            "session_id": x.get("name", "#"),
            "phone": x.get("phone", "#"),
            "title": x.get("title", "#"),
            "status": x.get("status", "#")
        })
    response_object['sesss'] = list_session
    return jsonify(response_object)



@app.route('/add_sess', methods=['GET', 'POST'])
async def root():
    # We want to update the global phone variable to remember it
    global phone
    global client
    global SESSION
    if client is None:
        # Telethon client
        client = TelegramClient(SESSION, API_ID, API_HASH)
        await client.connect()
    # Check form parameters (phone/code)
    form = await request.form
    response_object = {'status': 0}
    if 'phone' in form:
        title = form['title']
        phone = form['phone']
        phone = process_phone(phone)
        response_object.update({"phone": phone})
        phone_key = phone.replace("+", "")
        for x in mycol.find({"status": 1, "phone": phone_key}):
            phone = None
            response_object.update({"message": "Client is running!"})
            return jsonify(response_object)
        await client.send_code_request(phone)
        mydict = { "phone": phone_key, "name": SESSION, "title": title,  "status": 0 }
        mycol.insert_one(mydict)
        SESSION = str(uuid.uuid4().hex)
        response_object.update({"status": 1, "message": "Client is running!"})

    return jsonify(response_object)
    
     

    # # If we're logged in, show them some messages from their first dialog
    # if await client.is_user_authorized():
    #     # They are logged in, show them some messages from their first dialog
    #     # dialog = (await client.get_dialogs())[0]
    #     list_client.append(client)
    #     mydict = { "name": SESSION, "phone": phone, "status": 1 }
    #     SESSION = str(uuid.uuid4().hex)
    #     result = '<h1>{} {}</h1>'.format(len(list_client), "connected")
    #     x = mycol.insert_one(mydict)
    #     # async for m in client.get_messages(dialog, 10):
    #     #     result += await(format_message(m))
    #     client = None
    #     phone = None
    #     return await render_template_string(BASE_TEMPLATE, content=result)

    # # Ask for the phone if we don't know it yet
    # if phone is None:
    #     return await render_template_string(BASE_TEMPLATE, content=PHONE_FORM)

    # # We have the phone, but we're not logged in, so ask for the code
    # return await render_template_string(BASE_TEMPLATE, content=CODE_FORM)


@app.route('/verify-code', methods=['GET', 'POST'])
async def verifycode():
    # We want to update the global phone variable to remember it
    global phone
    global client
    global SESSION
    if client is None:
        # Telethon client
        client = TelegramClient(SESSION, API_ID, API_HASH)
        await client.connect()
    form = await request.form
    if 'code' in form:
        await client.sign_in(code=form['code'])
        if await client.is_user_authorized():
            phone = form['phone']
            filter = { 'phone': process_phone(phone).replace("+", "") }
            # Values to be updated.
            newvalues = { "$set": { 'status': 1 } }
            # Using update_one() method for single
            # updation.
            mycol.update_one(filter, newvalues)
            SESSION = str(uuid.uuid4().hex)
            client = None
            phone = None
            return jsonify({"phone": phone, "status": 1})
        return jsonify({"phone": phone, "status": 0})
    
@app.route('/add_foward', methods=['GET', 'POST'])
async def setting_foward():
    form = await request.form
    phone = form['phone']
    phone_key = process_phone(phone).replace("+", "")
    mess_from = form["from"]
    mess_to = form["to"]
    mydict = { "phone": phone_key, "from": mess_from,  "to": mess_to }
    forward_col.insert_one(mydict)


async def main():
    await hypercorn.asyncio.serve(app, hypercorn.Config())


# By default, `Quart.run` uses `asyncio.run()`, which creates a new asyncio
# event loop. Instead, we use `asyncio.run()` manually in order to make this
# explicit, as the client cannot be "transferred" between loops while
# connected due to the need to schedule work within an event loop.
#
# In essence one needs to be careful to avoid mixing event loops, but this is
# simple, as `asyncio.run` is generally only used in the entry-point of the
# program.
#
# To run Quart inside `async def`, we must use `hypercorn.asyncio.serve()`
# directly.
#
# This example creates a global client outside of Quart handlers.
# If you create the client inside the handlers (common case), you
# won't have to worry about any of this, but it's still good to be
# explicit about the event loop.
if __name__ == '__main__':
    asyncio.run(main())