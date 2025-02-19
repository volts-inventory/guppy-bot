import openai
import os
from core.template import template
import re
import trafilatura
import time
import pymongo


class Guppy:
    def __init__(self):
        openai.api_key = os.environ['OPENAPI_KEY']
        self.init_msg = [{"role": "system", "content": template}]
        self.users_to_msgs = {}
        self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        dblist = self.myclient.database_names()
        self.mydb = self.myclient["guppy"]
        self.mycol = self.mydb["convo"]
        if "guppy" in dblist:
            print("Loading old db")
            self.load_conversations()
        else:
            print("Creating new db")
            
    def load_conversations(self):
        cursor = self.mycol
        for document in cursor.find():
            speaker = document["speaker"]
            convo = document["convo_name"]
            convos = document["convos"]
            print(f"Loading speaker:{speaker} convo:{convo} length:{len(convos)}")
            for msg in convos:
                self.add_message_to_conversation(speaker, convo, msg, write=False)
            print("Load completed")  
    
    def clear_all_conversations(self):
        print("Deleting all records from DB")
        self.cols.delete_many({})

    def get_conversations(self, speaker):
        return self.users_to_msgs[speaker]["conversations"].keys()

    def get_conversation(self, speaker, convo_name):
        return self.users_to_msgs[speaker]["conversations"].get(convo_name)

    def new_conversation(self, speaker, convo_name, write=True):
        if speaker not in self.users_to_msgs:
            self.users_to_msgs[speaker] = {"conversations":{convo_name:[]}}
        else:
            self.users_to_msgs[speaker]["conversations"][convo_name] = []
        if write:
            self.mycol.insert_one({"speaker": speaker, "convo_name": convo_name, "convos":[]})

    def add_message_to_conversation(self, speaker, convo_name, msg, write=True):
        if speaker in self.users_to_msgs:
            if convo_name not in self.get_conversations(speaker): 
                self.new_conversation(speaker, convo_name, write) 
        else:
            self.new_conversation(speaker, convo_name, write)
        self.users_to_msgs[speaker]["conversations"][convo_name].append(msg)

        myquery = { "speaker":speaker, "convo_name": convo_name}
        newvalues = {'$push': {'convos': msg}}
        if write:
            self.mycol.update_one(myquery, newvalues)
    
    
    def converse(self, speaker, convo_name, query):
        if "http://" in query or "https://" in query:
            url = re.search("(?P<url>https?://[^\s]+)", query).group("url")
            ask = query.split("https://")[0]
            downloaded = trafilatura.fetch_url(url)
            web_text = trafilatura.extract(downloaded)
            query = f"{ask}: \'{web_text}\'"
        
        query = query.replace("\n", " ")
        query = ' '.join(query.split())
        print(query)
        self.add_message_to_conversation(speaker, convo_name, {"role":"user", "content":query})
            
        success = False
        engine = "gpt-4o" 
        buffer_len = -16
        while not success:
            try: 
                completions = openai.ChatCompletion.create(
                    model = engine,
                    messages = self.init_msg + self.get_conversation(speaker, convo_name)[buffer_len:],
                    max_tokens=200
                )
                success = True
            except Exception as e:
                time.sleep(5)
                pass
        print(engine)
        print(buffer_len)
        message = completions.choices[0].message.content
        print(message)
        self.add_message_to_conversation(speaker, convo_name, {"role": "assistant", "content": message})
        return message
