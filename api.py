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
from mongo import *
import uuid

# tele_account = mydb["accounts"] 
def get_env(name, message):
    if name in os.environ:
        return os.environ[name]
    return input(message)


# Session name, API ID and hash to use; loaded from environmental variables
# SESSION = os.environ.get('TG_SESSION', 'quart')
# API_ID = int(get_env('TG_API_ID', 'Enter your API ID: '))
# API_HASH = get_env('TG_API_HASH', 'Enter your API hash: ')

API_ID = "14225107" #os.getenv('api_id')
API_HASH = "bc6b2686eea4dc38f72181dd8d279dbf" #os.getenv('api_hash')
SESSION =  "84986626975"#os.getenv('STRING_SESSION')

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
    for x in DB_ACCOUNT.find({"status": 1}):
        print(x)
        session = x["name"]
        cl = TelegramClient(session, API_ID, API_HASH)
        await cl.connect()
        if await cl.is_user_authorized():
            list_client.append(cl)
        else:
            myquery = { "name":  session}
            newvalues = { "$set": { "status": 0 } }
            x = DB_ACCOUNT.update_many(myquery, newvalues)


# # After we're done serving (near shutdown), clean up the client
# @app.after_serving
# async def cleanup():
#     await client.disconnect()

@app.route('/session', methods=['GET', 'POST'])
async def all_session():
    list_session = []
    response_object = {'status': 'success'}
    for x in DB_ACCOUNT.find({}):
        list_session.append({
            "session_id": x.get("name", "#"),
            "phone": x.get("phone", "#"),
            "title": x.get("title", "#"),
            "status": x.get("status", "#")
        })
    response_object['sesss'] = list_session
    return jsonify(response_object)



@app.route('/sessions', methods=['GET', 'POST'])
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
    response_object = {'status': 0}
    if request.method == 'POST':
        # try:
        post_data = await request.get_json()
        phone = post_data.get('phone')
        code = post_data.get("code")
        task_id = post_data.get("task_id")
        cate_id = post_data.get('category_id')
        phone = process_phone(phone)
        response_object.update({"phone": phone})
        phone_key = phone.replace("+", "")
        if code is not None:
            await client.sign_in(code=post_data.get("code"))
            if await client.is_user_authorized():
                phone = post_data.get('phone')
                response_object.update({"phone": phone})
                filter = { 'phone': phone_key }
                newvalues = { "$set": { 'status': 1 } }
                DB_ACCOUNT.update_one(filter, newvalues)
                SESSION = str(uuid.uuid4().hex)
                client = None
                phone = None
                response_object.update({"status": 1, "message": "sussess"})
                return jsonify(response_object)
        elif task_id is not None:
            filter = { 'phone': phone_key }
            newvalues = { "$set": { "task_id": task_id , "category_id": cate_id} }
            DB_ACCOUNT.update_one(filter, newvalues)
            # task_id = post_data.get('task_id')
            # cate_id = post_data.get('category_id')
            # new_dict = { "phone": phone_key, "task_id": task_id }
            # query = { "name":  phone_key}
            # x = DB_ACCOUNT.update_many(query, new_dict)
            response_object.update({"status": 1, "message": "All done!"})
            return jsonify(response_object)
        else:
            x = DB_ACCOUNT.find_one({"phone": phone_key})
            if x is not None:
                if x.get("status", 0):
                    new_client = TelegramClient(x.get("name"), API_ID, API_HASH)
                    await new_client.connect()
                    if new_client.is_user_authorized():
                        phone = None
                        response_object.update({"message": "Client is running!"})
                        return jsonify(response_object)
                else:
                    task_id = post_data.get('task_id')
                    cate_id = post_data.get('category_id')
                    new_dict = { "$set": {"phone": phone_key, "task_id": task_id , "category_id": cate_id}}
                    query = { "name":  phone_key}
                    x = DB_ACCOUNT.update_many(query, new_dict)
                    response_object.update({"status": 1, "message": "All done!"})
                    return jsonify(response_object)
            await client.send_code_request(phone)
            mydict = { "name": SESSION, "phone": phone_key, "status": 0 }
            DB_ACCOUNT.insert_one(mydict)
            SESSION = str(uuid.uuid4().hex)
            response_object.update({"status": 1, "message": "Send code done!"})
            return jsonify(response_object)
        # except:
        #     response_object.update({"status": 0, "message": "Error!"})
        #     return jsonify(response_object)
    else:
        list_session = []
        response_object = {'status': 'success'}
        for x in DB_ACCOUNT.find({}):
            task = db_task.find_one({"id": x.get("task_id") })
            category = DB_CATEGORIES.find_one({"id": x.get("category_id")})
            data = {
                "id": x.get("name", "#"),
                "phone": x.get("phone", "#"),
                "status": x.get("status", "#")
            }
            if task is not None:
                data.update({"task": task.get("name", "#")})
            if category is not None:
                data.update({"category": category.get("name", "#")})
            list_session.append(data)
        return jsonify(list_session)

    
     

    # # If we're logged in, show them some messages from their first dialog
    # if await client.is_user_authorized():
    #     # They are logged in, show them some messages from their first dialog
    #     # dialog = (await client.get_dialogs())[0]
    #     list_client.append(client)
    #     mydict = { "name": SESSION, "phone": phone, "status": 1 }
    #     SESSION = str(uuid.uuid4().hex)
    #     result = '<h1>{} {}</h1>'.format(len(list_client), "connected")
    #     x = DB_ACCOUNT.insert_one(mydict)
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
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        await client.sign_in(code=post_data.get("code"))
        if await client.is_user_authorized():
            phone = post_data.get('phone')
            response_object.update({"phone": phone})
            filter = { 'phone': process_phone(phone).replace("+", "") }
            newvalues = { "$set": { 'status': 1 } }
            DB_ACCOUNT.update_one(filter, newvalues)
            SESSION = str(uuid.uuid4().hex)
            client = None
            phone = None
            response_object.update({"status": 1, "message": "sussess"})
            return jsonify(response_object)
    return jsonify({"status": 0, "message": "error"})

# @app.route('/update-session', methods=['GET', 'POST'])
# async def update_session():
#     response_object = {'status': 0}
#     if request.method == 'POST':
#         post_data = await request.get_json()
#         phone = process_phone(post_data.get('phone'))
#         response_object.update({"phone": phone})
#         task_id = post_data.get('task_id')
#         cate_id = post_data.get('category_id')
#         phone_key = phone.replace("+", "")
#         new_dict = { "phone": phone_key, "task_id": mess_from,  "cate_id": mess_to }
#         query = { "name":  phone_key}
#         x = DB_ACCOUNT.update_many(query, new_dict)
#         return jsonify(response_object)

@app.route('/task', methods=['GET', 'POST'])
async def taks():
    return jsonify({"id": 1, "name": "Crawl"}, {"id": 2, "name": "Poster"})

@app.route('/categories', methods=['GET', 'POST'])
async def categories():
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        cate_name = post_data.get("name")
        type_id = post_data.get("type_id")
        mydict = { "id": str(uuid.uuid4().hex), "name": cate_name, "type_id": type_id}
        DB_CATEGORIES.insert_one(mydict)
        response_object = {'status': 1}
        return jsonify(response_object)
    else:
        list_cate_results = []
        data = request.args.to_dict(flat=True)
        type_id = data.get("type_id")
        query = {}
        if type_id is not None:
            query.update({"type_id": type_id})
        cate_for = data.get("cate_for")
        if cate_for is not None:
            query.update({"cate_for": cate_for})
        list_cates = list(DB_CATEGORIES.find(query))
        # print(query)
        for x in list_cates:
            if x.get("type_id") is None:
                continue
            typef = db_task.find_one({"id": str(x["type_id"])})
            if typef is not None:
                type_name = typef.get("name")
                x["type"] = type_name
                x.pop("_id")
                list_cate_results.append(x)
        return jsonify(list_cate_results)

# @app.route('/categories-word', methods=['GET', 'POST'])
# async def categories_world():
#     response_object = {'status': 0}
#     if request.method == 'POST':
#         post_data = await request.get_json()
#         cate_name = post_data.get("name")
#         mydict = { "id": str(uuid.uuid4().hex), "name": cate_name}
#         DB_CATEGORIES_world.insert_one(mydict)
#         response_object = {'status': 1}
#         return jsonify(response_object)
#     else:
#         list_cates = []
#         for x in DB_CATEGORIES_world.find({}):
#             list_cates.append({
#                 "id": x.get("id"),
#                 "name": x.get("name"),
#             })
#         return jsonify(list_cates)

@app.route('/keywords', methods=['GET', 'POST'])
async def keyword():
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        keywords = post_data.get("keywords").split("|")
        cate_id = post_data.get("cate_id")
        if keywords is not None:
            for keyword in keywords:
                mydict = { "id": str(uuid.uuid4().hex), "keyword": keyword, "category_id": cate_id}
                DB_KEYWORD.insert_one(mydict)
        response_object = {'status': 1}
        return jsonify(response_object)
    else:
        get_data = request.args.to_dict(flat=True)
        cat_id = get_data.get("cat_id")
        if cat_id is not None:
            list_keyword = list(DB_KEYWORD.find({"category_id": cat_id}))
        else:
            list_keyword = list(DB_KEYWORD.find({}))
        category_name = ""
        list_results = []
        for x in list_keyword:
            category = DB_CATEGORIES.find_one({"id": x["category_id"]})
            if category is not None:
                category_name = category.get("name")
                x["category"] = category_name
                x.pop("_id")
                list_results.append(x)
        return jsonify(list_results)


@app.route('/replace-words', methods=['GET', 'POST'])
async def replace_words():
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        word = post_data.get("words")
        replace = post_data.get("replace")
        cate_id = post_data.get("cate_id")
        mydict = { "id": str(uuid.uuid4().hex), "word": word, "replace": replace, "category_id": cate_id}
        DB_REPLACE_WORD.insert_one(mydict)
        response_object = {'status': 1}
        return jsonify(response_object)
    else:
        get_data = request.args
        cat_id = get_data.get("cat_id")
        if cat_id is not None:
            list_keyword = list(DB_REPLACE_WORD.find({"category_id": cat_id}))
        else:
            list_keyword = list(DB_REPLACE_WORD.find({}))
        category_name = ""
        list_results = []
        for x in list_keyword:
            category = DB_CATEGORIES.find_one({"id": x["category_id"]})
            if category is not None:
                category_name = category.get("name")
                x["category"] = category_name
                x.pop("_id")
                list_results.append(x)
        return jsonify(list_results)
    

@app.route('/get_category', methods=['GET'])
async def get_category():
    # data = request.args
    # print(data.get("id"))
    return jsonify([{"id": 1, "name":"share keo"}, {"id": 2, "name":"ca do"}]) 


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