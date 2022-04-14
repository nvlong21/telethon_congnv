import base64
import os
import hypercorn.asyncio
from quart import Quart, jsonify, render_template_string, request
from quart_cors import cors
import asyncio
from loguru import logger
from telethon.tl.patched import MessageService
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon import TelegramClient, utils
from mongo import *
import uuid
from multiprocessing.dummy import Process, Queue
import service

logger.add("logs/file_1.log", rotation="500 MB")
def get_env(name, message):
    if name in os.environ:
        return os.environ[name]
    return input(message)
# Session name, API ID and hash to use; loaded from environmental variables
#
# API_ID = int(get_env('TG_API_ID', 'Enter your API ID: '))
# API_HASH = get_env('TG_API_HASH', 'Enter your API hash: ')

API_ID = "14225107" #os.getenv('api_id')
API_HASH = "bc6b2686eea4dc38f72181dd8d279dbf" #os.getenv('api_hash')
SESSION =  "84986626975"#os.getenv('STRING_SESSION')

# Quart app
app = Quart(__name__)
app.secret_key = 'CHANGE THIS TO SOMETHING SECRET'
app = cors(app, allow_origin="*")

def process_phone(phone):
    return phone.replace(" ", "").replace("(", "").replace(")", "")


# # Connect the client before we start serving with Quart
@app.before_serving
async def startup():
    for x in DB_ACCOUNT.find():
        try:
            session = x["phone"]
            cl = TelegramClient(session, API_ID, API_HASH)
            await cl.connect()
            if await cl.is_user_authorized():
                logger.info("Client {} activate!".format(str(session)))
                service.CLIENTS[session] = cl
            else:
                myquery = { "phone":  session}
                newvalues = { "$set": { "status": "not author" } }
                x = DB_ACCOUNT.update_many(myquery, newvalues)
                logger.info("Client {} not author!".format(str(session)))
        except Exception as e:
            logger.error(str(e))

# # After we're done serving (near shutdown), clean up the client
@app.after_serving
async def cleanup():
    for k in service.CLIENTS.keys():
        await service.CLIENTS[k].disconnect()

@app.route('/session/<id>', methods=['DELETE'])
async def delete_session(id):
    query = {"id": str(id)}
    DB_ACCOUNT.delete_many(query)
    return jsonify({"message": "success", "status": 1})

@app.route('/sessions', methods=['GET', 'POST'])
async def root():
    # We want to update the global phone variable to remember it
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        phone = post_data.get('phone')
        code = post_data.get("code")
        task_id = post_data.get("task_id")
        cate_id = post_data.get('category_id')
        phone = process_phone(phone)
        response_object.update({"phone": phone})
        phone_key = phone.replace("+", "")
        client = service.CLIENTS.get(phone_key, None)
        try:
            if client is None:
                client = TelegramClient(phone_key, API_ID, API_HASH)
                await client.connect()
                service.CLIENTS[phone_key] = client
                if await client.is_user_authorized():
                    x = DB_ACCOUNT.find_one({"phone": phone_key})
                    if x is None:
                        mydict = {"phone": phone_key, "status": "live"}
                        DB_ACCOUNT.insert_one(mydict)
                    return jsonify({"message": "Client is exist!", "status": 2})

            if code is not None:
                await client.sign_in(code=post_data.get("code"))
                if await client.is_user_authorized():
                    phone = post_data.get('phone')
                    response_object.update({"phone": phone})
                    filter = { 'phone': phone_key }
                    newvalues = { "$set": { 'status': "live" } }
                    DB_ACCOUNT.update_one(filter, newvalues)
                    response_object.update({"status": 1, "message": "sussess"})
                    return jsonify(response_object)
            elif task_id is not None:
                filter = { 'phone': phone_key }
                newvalues = { "$set": { "task_id": task_id , "category_id": cate_id} }
                DB_ACCOUNT.update_one(filter, newvalues)

                response_object.update({"status": 1, "message": "All done!"})
                return jsonify(response_object)
            else:
                x = DB_ACCOUNT.find_one({"phone": phone_key})
                if x is not None:
                    if x.get("status") is not None:
                        new_client = TelegramClient(x.get("phone"), API_ID, API_HASH)
                        await new_client.connect()
                        if await new_client.is_user_authorized():
                            response_object.update({"message": "Client is running!", "status": 2 })
                            return jsonify(response_object)
                    # else:
                    #     task_id = post_data.get('task_id')
                    #     cate_id = post_data.get('category_id')
                    #     new_dict = { "$set": {"phone": phone_key, "task_id": task_id , "category_id": cate_id}}
                    #     query = { "phone":  phone_key}
                    #     x = DB_ACCOUNT.update_many(query, new_dict)
                    #     response_object.update({"status": 1, "message": "All done!"})
                    #     return jsonify(response_object)

                await client.send_code_request(phone)
                account_entrie = DB_ACCOUNT.find_one({"phone": phone_key})
                if account_entrie is None:
                    mydict = {"phone": phone_key, "status": "live"}
                    DB_ACCOUNT.insert_one(mydict)
    
                response_object.update({"status": 1, "message": "Send code done!"})
                return jsonify(response_object)
        except Exception as e:
            if phone_key in service.CLIENTS.keys():
                service.CLIENTS.pop(phone_key)
                new_dict = { "$set": {"status": 1}}
                query = { "phone":  phone_key}
                x = DB_ACCOUNT.update_many(query, new_dict)
            return jsonify({"message": str(e), "status": 0})
    elif request.method == 'GET':
        try:
            list_session = []
            response_object = {'status': 1}
            for x in DB_ACCOUNT.find({}):
                task = DB_TASK.find_one({"id": x.get("task_id") })
                category = DB_CATEGORIES.find_one({"id": x.get("category_id")})
                data = {
                    "id": x.get("id", "#"),
                    "phone": x.get("phone", "#"),
                    "status": x.get("status", "#")
                }
                if task is not None:
                    data.update({"task": task.get("name", "#")})
                if category is not None:
                    data.update({"category": category.get("name", "#")})
                list_session.append(data)
            return jsonify(list_session)
        except:
            return jsonify({"message": "error", "status": 0})


# @app.route('/verify-code', methods=['GET', 'POST'])
# async def verifycode():
#     # We want to update the global phone variable to remember it
#     global phone
#     global client
#     global SESSION
#     if client is None:
#         # Telethon client
#         client = TelegramClient(SESSION, API_ID, API_HASH)
#         await client.connect()
#     response_object = {'status': 0}
#     if request.method == 'POST':
#         post_data = await request.get_json()
#         await client.sign_in(code=post_data.get("code"))
#         if await client.is_user_authorized():
#             phone = post_data.get('phone')
#             response_object.update({"phone": phone})
#             filter = { 'phone': process_phone(phone).replace("+", "") }
#             newvalues = { "$set": { 'status': 1 } }
#             DB_ACCOUNT.update_one(filter, newvalues)
#             SESSION = str(uuid.uuid4().hex)
#             client = None
#             phone = None
#             response_object.update({"status": 1, "message": "sussess"})
#             return jsonify(response_object)
#     return jsonify({"status": 0, "message": "error"})


@app.route('/init-exam', methods=['GET', 'POST'])
async def init_exam():
    test_db()
    return jsonify({"status": 1})


@app.route('/task', methods=['GET', 'POST'])
async def taks():
    return jsonify({"id": 1, "name": "Crawl"}, {"id": 2, "name": "Poster"})

@app.route('/categorie/<id>', methods=['DELETE'])
async def delete_categorie(id):
    query = {"id": str(id)}
    d = DB_CATEGORIES.delete_many(query)
    return jsonify({"message": "success", "status": 1})


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
            if int(type_id)<=2:
                list_cate_results.append({"id": ALL_CATEGORIES, "type": '#', "name": "All"})
            query.update({"type_id": type_id})
        else:
            list_cate_results.append({"id": ALL_CATEGORIES, "type": '#', "name": "All"})
        cate_for = data.get("cate_for")
        if cate_for is not None:
            query.update({"cate_for": cate_for})
        list_cates = list(DB_CATEGORIES.find(query))
        # print(query)
        for x in list_cates:
            if x.get("type_id") is None:
                continue
            typef = DB_TASK.find_one({"id": str(x["type_id"])})
            if typef is not None:
                type_name = typef.get("name")
                type_id = typef.get("id")
                x["type"] = type_name
                x["type_id"] = type_id
                x.pop("_id")
                list_cate_results.append(x)
        return jsonify(list_cate_results)

@app.route('/keyword/<id>', methods=['DELETE'])
async def delete_keyword(id):
    query = {"id": str(id)}
    d = DB_KEYWORD.delete_many(query)
    return jsonify({"message": "success", "status": 1})


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

@app.route('/remove-word/<id>', methods=['DELETE'])
async def delete_remove_word(id):
    query = {"id": str(id)}
    d = DB_STOPWORD.delete_many(query)
    return jsonify({"message": "success", "status": 1})


@app.route('/remove-words', methods=['GET', 'POST'])
async def remove_word():
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        remove_words = post_data.get("remove_words").split("|")
        cate_id = post_data.get("cate_id")
        if remove_words is not None:
            for remove_word in remove_words:
                mydict = { "id": str(uuid.uuid4().hex), "stop_word": remove_word, "category_id": cate_id}
                DB_STOPWORD.insert_one(mydict)
        response_object = {'status': 1}
        return jsonify(response_object)
    else:
        get_data = request.args.to_dict(flat=True)
        cat_id = get_data.get("cat_id")
        if cat_id is not None:
            list_remove_word = list(DB_STOPWORD.find({"category_id": cat_id}))
        else:
            list_remove_word = list(DB_STOPWORD.find({}))
        category_name = ""
        list_results = []
        for x in list_remove_word:
            category = DB_CATEGORIES.find_one({"id": x["category_id"]})
            if category is not None:
                category_name = category.get("name")
                x["category"] = category_name
                x.pop("_id")
                list_results.append(x)
        return jsonify(list_results)


@app.route('/replace-word/<id>', methods=['DELETE'])
async def delete_replace_word(id):
    query = {"id": str(id)}
    d = DB_REPLACE_WORD.delete_many(query)
    return jsonify({"message": "success", "status": 1})
   


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

@app.route('/craw-process/<id>', methods=['DELETE'])
async def delete_crawl_process(id):
    query = {"id": str(id)}
    d = DB_CRAWL.delete_many(query)
    return jsonify({"message": "success", "status": 1})
    


@app.route('/craw-process', methods=['GET', 'POST'])
async def crawl_process():
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        get_froms = post_data.get("froms").split("|")
        from_type = post_data.get("type")
        cate_id = post_data.get("category_crawl")
        category_keyword_id = post_data.get("category_keyword_id")
        category_stopword_id = post_data.get("category_stopword_id")
        category_post_id = post_data.get("category_post_id")
        category_replace_id = post_data.get("category_replace_id")
        for fr in get_froms:
            mydict = { "id": str(uuid.uuid4().hex), "from": fr.replace(" ", ""), "type": from_type, "category_id": cate_id,
                "category_keyword_id": category_keyword_id, "category_stopword_id": category_stopword_id, "category_post_id": category_post_id,
                "category_replace_id": category_replace_id, "offset": 0}
            DB_CRAWL.insert_one(mydict)
        response_object = {'status': 1}
        return jsonify(response_object)
    else:
        get_data = request.args
        cat_id = get_data.get("cat_id")
        if cat_id is not None:
            list_crawl_process = list(DB_CRAWL.find({"category_id": cat_id}))
        else:
            list_crawl_process = list(DB_CRAWL.find({}))
        category_name = ""
        list_results = []

        for x in list_crawl_process:
            x.pop("_id")
            category = DB_CATEGORIES.find_one({"id": x["category_id"]})
            if category is not None:
                category_name = category.get("name")
                x["category_crawl"] = category_name
                x["category_crawl_id"] = category.get("id")

            category_keyword = DB_CATEGORIES.find_one({"id": x["category_keyword_id"]})
            if category_keyword is not None:
                category_keyword_name = category_keyword.get("name")
                x["category_word"] = category_keyword_name
                x["category_word_id"] = category_keyword.get("id")
            category_stopword = DB_CATEGORIES.find_one({"id": x["category_stopword_id"]})
            if category_stopword is not None:
                category_stopword_name = category_stopword.get("name")
                x["category_stopword"] = category_stopword_name
                x["category_stopword_id"] = category_stopword.get("id")
            
            
            category_post = DB_CATEGORIES.find_one({"id": x["category_post_id"]})
            if category_post is not None:
                category_post_name = category_post.get("name")
                x["category_post"] = category_post_name
                x["category_post_id"] = category_post.get("id")

            category_replace = DB_CATEGORIES.find_one({"id": x["category_replace_id"]})
            if category_replace is not None:
                category_replace_name = category_replace.get("name")
                x["category_replace_word"] = category_replace_name
                x["category_replace_word_id"] = category_replace.get("id")
            list_results.append(x)
        return jsonify(list_results)

@app.route('/post-process/<id>', methods=['DELETE'])
async def delete_post_process(id):
    query = {"id": str(id)}
    d = DB_POST.delete_many(query)
    return jsonify({"message": "success", "status": 1})
    


@app.route('/post-process', methods=['GET', 'POST'])
async def post_process():
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        posts_to = post_data.get("posts_to").split("|")
        _type = post_data.get("type")
        cate_id = post_data.get("category_post")

        for post_to in posts_to:
            mydict = { "id": str(uuid.uuid4().hex), "post_to": post_to.replace(" ", ""), "type": _type, "category_id": cate_id}
            DB_POST.insert_one(mydict)
        response_object = {'status': 1}
        return jsonify(response_object)
    else:
        get_data = request.args
        cat_id = get_data.get("cat_id")
        if cat_id is not None:
            list_post_process = list(DB_POST.find({"category_id": cat_id}))
        else:
            list_post_process = list(DB_POST.find({}))
        category_name = ""
        list_results = []

        for x in list_post_process:
            x.pop("_id")
            category = DB_CATEGORIES.find_one({"id": x["category_id"]})
            if category is not None:
                category_name = category.get("name")
                x["category_post"] = category_name
                x["category_post_id"] = category.get("id")
            list_results.append(x)
        return jsonify(list_results)


@app.route('/reload-db', methods=['GET'])
async def reload_db():
    service.INIT = False
    return jsonify({"status": "done"}) 


# @app.route('/get_category', methods=['GET'])
# async def get_category():
#     # data = request.args
#     # print(data.get("id"))
#     return jsonify([{"id": 1, "name":"share keo"}, {"id": 2, "name":"ca do"}]) 


async def main():
    config = hypercorn.Config()
    config =  hypercorn.Config.from_pyfile("./config.py")
    await hypercorn.asyncio.serve(app, config)


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
    # run_init()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # loop = asyncio.get_event_loop()
    loop.create_task(service.Sender())
    loop.create_task(main())
    Process(loop.run_until_complete(service.Crawl())).run()
    
    # asyncio.run(main())