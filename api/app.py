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
import glob
import subprocess
logger.add("logs/api/{time:YYYY-MM-DD}_1.log", rotation="500 MB")
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
CLIENTS = {}
# Quart app
app = Quart(__name__)
app.secret_key = 'CHANGE THIS TO SOMETHING SECRET'
app = cors(app, allow_origin="*")

def process_phone(phone):
    return phone.replace(" ", "").replace("(", "").replace(")", "")

# # Connect the client before we start serving with Quart
@app.before_serving
async def startup():
    pass
# # After we're done serving (near shutdown), clean up the client
@app.after_serving
async def cleanup():
    for k in CLIENTS.keys():
        await CLIENTS[k].disconnect()

@app.route('/session/<phone>', methods=['DELETE'])
async def delete_session(phone):
    query = {"phone": str(phone)}
    x = DB_ACCOUNT.find_one(query)
    if x is not None:
        DB_ACCOUNT.delete_many(query)
    phone = process_phone(phone)  
    phone_key = phone.replace("+", "")
    subprocess.run(["rm", "-f", "{}.session".format(phone_key)])
    return jsonify({"message": "success", "status": 1})

@app.route('/sessions-upload', methods=['POST'])
async def sessions_upload():
    files = await request.files
    form = await request.form
    task_id = form.get("task_id")
    cate_id = form.get('category_id')
    response_object = {}
    message = {}
    for k in files.keys():
        try:
            if k.startswith("file"):
                file = files.get(k)
                if file and file.filename:
                    await file.save(file.filename)
                    phone = file.filename.split(".")[0]
                    phone = process_phone(phone)
                    phone_key = phone.replace("+", "")
                    query = {"phone": str(phone_key)}
                    client_name = DB_ACCOUNT.find_one(query)
                    if client_name is None or (client_name.get("status") != "live"):
                        client = TelegramClient(phone_key, API_ID, API_HASH)
                        try:
                            await client.connect()
                            if await client.is_user_authorized():
                                if client_name is None:
                                    mydict = {"id": str(uuid.uuid4().hex), "task_id": task_id , "category_id": cate_id, "phone": phone_key, "status": "live"}
                                    DB_ACCOUNT.insert_one(mydict)
                                else:
                                    filter = { 'phone': phone_key }
                                    newvalues = { "$set": { "task_id": task_id , "category_id": cate_id, "status": "live"} }
                                    DB_ACCOUNT.update_one(filter, newvalues)
                                # response_object.update({"status": "1", "message": "success"})
                                
                                message.update({phone_key: "success"})
                                client.disconnect()
                            else:
                                if client_name is None:
                                    mydict = {"id": str(uuid.uuid4().hex), "task_id": task_id , "category_id": cate_id, "phone": phone_key, "status": "Not activated"}
                                    DB_ACCOUNT.insert_one(mydict)
                                else:
                                    filter = { 'phone': phone_key }
                                    newvalues = { "$set": { "task_id": task_id , "category_id": cate_id, "status": "Not activated"} }
                                    DB_ACCOUNT.update_one(filter, newvalues)
                                message.update({phone_key: "Not activate"})
                        except Exception as e:
                            message.update({phone_key: str(e)})
                            # status =  0
                            # response_object.update({"status": "0", "message": str(e)})
                    else:
                        message.update({phone_key: "Exist!"})
            response_object.update({"status": "1", "message": "success", "logs": message})
        except Exception as e1:
            response_object.update({"status": "1", "message": str(e1), "logs": message})
    
    return jsonify(response_object)


@app.route('/sessions', methods=['GET', 'POST'])
async def sessions():
    # We want to update the global phone variable to remember it
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        phone = post_data.get('phone')
        phone = process_phone(phone)
        response_object.update({"phone": phone})
        phone_key = phone.replace("+", "")
        query = {"phone": str(phone_key)}
        client_name = DB_ACCOUNT.find_one(query)
        try:
            if client_name is None or (client_name.get("status")!="live"):
                client = TelegramClient(phone_key, API_ID, API_HASH)
                await client.connect()
                CLIENTS[phone_key] = client
                if await CLIENTS[phone_key].is_user_authorized():
                    mydict = {"phone": phone_key, "status": "live"}
                    DB_ACCOUNT.insert_one(mydict)
                    response_object.update({"status": 2, "message": "Client is exists!"})
                    await CLIENTS[phone_key].disconnect()
                else:
                    await CLIENTS[phone_key].send_code_request(phone)
                    mydict = {"phone": phone_key, "status": "not author"}
                    DB_ACCOUNT.insert_one(mydict)
                    response_object.update({"status": 1, "message": "Send code done!"})
            else:
                response_object.update({"status": 2, "message": "Client is exists!"})
            return jsonify(response_object)
    
        except Exception as e:
            if phone_key in CLIENTS.keys():
                CLIENTS.pop(phone_key)
                new_dict = { "$set": {"status": "not author"}}
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
                    "status": x.get("status", "not activate")
                }
                if task is not None:
                    data.update({"task": task.get("name", "#")})
                if category is not None:
                    data.update({"category": category.get("name", "#")})
                list_session.append(data)
            return jsonify(list_session)
        except:
            return jsonify({"message": "error", "status": 0})

@app.route('/sessions-code', methods=['GET', 'POST'])
async def sessions_code():
    # We want to update the global phone variable to remember it
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        phone = post_data.get('phone')
        phone = process_phone(phone)
        code = post_data.get("code")
        response_object.update({"phone": phone})
        phone_key = phone.replace("+", "")
        try:
            if phone_key in CLIENTS.keys():
                query = {"phone": str(phone_key)}
                client_name = DB_ACCOUNT.find_one(query)
                if await CLIENTS[phone_key].is_user_authorized():
                    if client_name is None:
                        mydict = {"id": str(uuid.uuid4().hex), "phone": phone_key, "status": "live"}
                        DB_ACCOUNT.insert_one(mydict)
                        response_object.update({"status": 2, "message": "Client is activate"})
                    else:
                        if client_name.get("status") == "live":
                            return jsonify({"message": "Client is exist!", "status": 2})
                        else:
                            newvalues = { "$set": { "task_id": task_id , "category_id": cate_id, "status": "live"} }
                            DB_ACCOUNT.update_one(query, newvalues)
                    await CLIENTS[phone_key].disconnect()
                else:
                    if code is not None:
                        await CLIENTS[phone_key].sign_in(code=code)
                        if await CLIENTS[phone_key].is_user_authorized():
                            newvalues = { "$set": { 'status': "live" } }
                            DB_ACCOUNT.update_one(query, newvalues)
                            response_object.update({"status": 2, "message": "sussess"})
                            CLIENTS[phone_key].disconnect()
                        else:
                            newvalues = { "$set": { 'status': "not author" } }
                            DB_ACCOUNT.update_one(query, newvalues)
                            response_object.update({"status": 0, "message": "Code is not correct!"})
                    else:
                        response_object.update({"status": 0, "message": "Code error"})
            else:
                response_object.update({"message": "please get code"})
            return jsonify(response_object)

        except Exception as e:
            if phone_key in CLIENTS.keys():
                CLIENTS.pop(phone_key)
                new_dict = { "$set": {"status": "not author"}}
                query = { "phone":  phone_key}
                x = DB_ACCOUNT.update_many(query, new_dict)
            return jsonify({"message": str(e), "status": 0})

@app.route('/sessions-task', methods=['GET', 'POST'])
async def sessions_task():
    # We want to update the global phone variable to remember it
    response_object = {'status': 0}
    if request.method == 'POST':
        post_data = await request.get_json()
        phone = post_data.get('phone')
        phone = process_phone(phone)
        task_id = post_data.get("task_id")
        cate_id = post_data.get('category_id')
        response_object.update({"phone": phone})
        phone_key = phone.replace("+", "")
        try:
            # if phone_key in CLIENTS.keys():
            if task_id is not None:
                filter = { 'phone': phone_key }
                newvalues = { "$set": { "task_id": task_id , "category_id": cate_id} }
                DB_ACCOUNT.update_one(filter, newvalues)
                response_object.update({"status": 1, "message": "All done!"})
            else:
                response_object.update({"status": 0, "message": "task id is null"})
            return jsonify(response_object)

        except Exception as e:
            if phone_key in CLIENTS.keys():
                CLIENTS.pop(phone_key)
                new_dict = { "$set": {"status": "not author"}}
                query = { "phone":  phone_key}
                x = DB_ACCOUNT.update_many(query, new_dict)
            return jsonify({"message": str(e), "status": 0})

@app.route('/init-exam', methods=['GET', 'POST'])
async def init_exam():
    test_db()
    return jsonify({"message": "success", "status": 1})


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
        response_object = {"message": "success", 'status': 1}
        return jsonify(response_object)
    else:
        list_cate_results = []
        data = request.args.to_dict(flat=True)
        type_id = data.get("type_id")
        query = {}
        if type_id is not None:
            query.update({"type_id": type_id})
        # else:
        #     list_cate_results.append({"id": ALL_CATEGORIES, "type": '#', "name": "All"})
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
        response_object = {"message": "success", 'status': 1}
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
        response_object = {"message": "success", 'status': 1}
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
        response_object = {"message": "success", 'status': 1}
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
        cate_id = post_data.get("cate_id")
        category_keyword_id = post_data.get("category_keyword_id")
        category_stopword_id = post_data.get("category_stopword_id")
        category_post_id = post_data.get("category_post_id")
        category_replace_id = post_data.get("category_replace_id")
        for fr in get_froms:
            mydict = { "id": str(uuid.uuid4().hex), "from": fr.replace(" ", ""), "type": from_type, "category_id": cate_id,
                "category_keyword_id": category_keyword_id, "category_stopword_id": category_stopword_id, "category_post_id": category_post_id,
                "category_replace_id": category_replace_id, "offset": 0}
            DB_CRAWL.insert_one(mydict)
        response_object = {"message": "success", 'status': 1}
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
        response_object = {"message": "success", 'status': 1}
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
    new_dict = { "$set": { "status_crawl": "1", "status_sender": "1"}}
    query = { "name": "reload"}
    DB_LOG.update_many(query, new_dict)
    return jsonify({"status": "done"}) 

@app.route('/get-list-log', methods=['GET'])
async def get_list_log():
    get_data = request.args
    log_task = get_data.get("log_task")
    list_log_file = glob.glob("./logs/{}/*.log".format(log_task))
    result = []
    for log_file in list_log_file:
        log_name = log_file.split("/")[-1].split(".")[0]
        result.append(log_name)
    return jsonify(result) 

@app.route('/get-log-data', methods=['POST'])
async def get_data_log():

    post_data = await request.get_json()
    log_task = post_data.get("log_task")
    log_file = post_data.get("log_file")
    from_line = post_data.get("from", 0)
    if from_line == "" or from_line is None:
        from_line = 0
    size = post_data.get("size")
    if size == "" or size is None:
        size = 100
    result = []
    with open("./logs/{}/{}.log".format(log_task, log_file), "r") as f:
        lines = f.readlines()
        for line in lines[int(from_line): int(from_line) + int(size)]:
            result.append({"log_info": line})
    return jsonify(result) 


async def main():
    config = hypercorn.Config()
    config =  hypercorn.Config.from_pyfile("./config.py")
    await hypercorn.asyncio.serve(app, config)

if __name__ == '__main__':
    asyncio.run(main())