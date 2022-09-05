
from __future__ import annotations
import json
import sys
from nltk.corpus import wordnet
import nltk

nltk.download('wordnet')
nltk.download('omw-1.4')
sys.path.insert(1, "/Users/***/Documents/Code/overclaim_tap/stanford_parser")
from stanford_parser import *


## generate 
read_access = ['read', 'see', 'image', 'run_across', 'construe', 'check', 'take', 'reckon', 'get_word', 'pick_up', 'watch', 'escort', 'figure', 'visualize', 'study', 'date', 'see_to_it', 'go_steady', 'record', 'consider', 'visualise', 'experience', 'view', 'get_wind', 'fancy', 'control', 'determine', 'understand', 'realise', 'hear', 'show', 'catch', 'visit', 'regard', 'run_into', 'take_in', 'read', 'look', 'examine', 'attend', 'interpret', 'go_out', 'ensure', 'meet', 'go_through', 'witness', 'scan', 'get_a_line', 'come_across', 'register', 'find_out', 'envision', 'see', 'realize', 'encounter', 'project', 'insure', 'assure', 'say', 'discover', 'find', 'picture', 'learn', 'take_care', 'translate', 'ascertain']
#read_access = ["read", "see"]
## generate  
write_access = ['publish', 'produce', 'write', 'create', 'save', 'indite', 'drop_a_line', 'compose', 'spell', 'make', 'pen']
#write_access = ["write", "create"]
## 
del_access =  ['delete', 'remove', 'take', 'edit', 'delete', 'blue-pencil', 'slay', 'get_rid_of', 'murder', 'polish_off', 'hit', 'withdraw', 'transfer', 'take_out', 'absent', 'erase', 'dispatch', 'take_away', 'off', 'cancel', 'bump_off', 'move_out']
#del_access = ["delete", "remove"]
## generate 
append_access = ['append','change','interchange', 'affix', 'supply', 'alteration', 'switch', 'convert', 'alter', 'modify', 'tag_on', 'vary', 'add_on', 'qualify', 'modified', 'shift', 'tack_on', 'transfer', 'variety', 'limited', 'hang_on', 'exchange', 'modification', 'commute', 'add', 'tack', 'deepen', 'append', 'supplement', 'change']
#append_access = ["append", "modify", "modified", "change"]

channel_id_permission_log_dict = dict()
channel_ = dict()


## these are tools


## get the corresponding file name: key:channel_id \t value:the file name
def load_channel_id_permission_log():
    file_name = "/Users/***/Documents/Code/overclaim_tap/database/channel_.txt"
    lines = open(file_name, "r").readlines()
    for line in lines:
        tks = line.replace("\n", "").split(" ")
        if len(tks) < 2:
            continue
        channel_id_permission_log_dict[tks[0]] = "___channels_" + tks[len(tks)-1] + "__phase2"
        channel_id_name[tks[0]] = tks[-1]

def process_word(word_list):
    ext = []
    for word in word_list:
        sim = find_similar_word(word)
        ext.extend(sim)
    ext = set(ext)
    print(ext)


def find_similar_word(word):
    syns = wordnet.synsets(word)
    sim_words = []
    for syn in syns:
        for l in syn.lemmas():
            sim_words.append(l.name())
    # sim_words = set(sim_words)
    return sim_words

def action_para(field):
    params = []
    name = field["name"].replace("_"," ")
    label = field["label"].lower()
    slug = field["slug"].replace("_", "")
    f_type = field["normalized_field_type"]
    required = field["required"]
    can_have_default = field["can_have_default"]
    return name, label, slug

def process_trigger(trigger):
    trigger_name = trigger["name"]
    verb, potential = parse_sentence_veb(trigger_name)
    verb.extend()

    return verb

def process_query(query):
    query_name = query["name"]
    return 



def process_action(channel_f, action):
    action_name = action["name"]
    action_des = action["description"]
    user_readable = action["verbage_for_user"]
    fields = action["action_fields"]    


    api_code = action["full_module_name"].split(".")[1].replace("_", " ")
    params = []
    for field in fields:
        name,label ,slug, = action_para(field)
        params.append(label)

    #print("#########################################")
    return action_name.lower()
    #print(action_des)


def word_similarity(word1, word2):
    verb1 = wordnet.synset('{}.v.01'.format(word1))
    verb2 = wordnet.synset('{}.v.01'.format(word2))

    # print(verb1)
    # print(verb2)
    print(verb1.path_similarity(verb2))
    return 

## purpose of this func, retrive possible nn relative to the corresponding api call 
## this nn would be used to filter the potential auth permission in oauth 


def text_split(text):
    ## 
    if text is None:
        return []
    text = str(text)
    if ' ' in text:
        return text.lower().split(' ')

    copy_text = text
    for cha in text:
        if cha.isupper():
            copy_text = copy_text + '_' + cha
        else:
            copy_text += cha

   
    text = text.lower()
    return text.split('_')
    
def get_operation_parameters(operation, mark):
    
    fetched_field = dict()
    if mark == "trigger":
        fetched_field["ingredients"] = ["slug", "note"]
        fetched_field["trigger_fields"] = ["slug", "label"]

    if mark == "query":
        fetched_field["ingredients"] = ["slug", "note"]
        fetched_field["query_fields"] = ["slug", "label"]
        
    
    if mark == "action":
        fetched_field["action_fields"] = ["slug" , "label"]


    params = []
    for key_1 in fetched_field:
        f_1 = operation[key_1]
        if f_1 is None or len(f_1) == 0:
            continue
        params = []

        for ele in f_1:
            for key_2 in fetched_field[key_1]:
                text = ele[key_2]
                if text is None:
                    continue
                if len(text) == 0:
                    continue
                params.append(' '.join(text_split(text)))
    
    return params

def preprocess_operations(operations, mark):
    trigger_heads = [
        "this trigger fires when", 
        "this trigger fires every time when", 
        "this trigger fires every time", 
        "this trigger fires",

        "this trigger fire every time",



        "the trigger fires every time",
        "the trigger fires when",


        "this triggers fires when",
        "this triggers fires every time",
        "this triggers when",

        "triggers when",
        "triggered when",

        "this trigger is fired every time",
        "this trigger is fired when",
        "this trigger is triggered when",

        "this trigger will fire every time",
        "this trigger will fires when",
        "this trigger runs every time",
        "this trigger works when",
        

        "this trigger when",
        "this triggers fire every time",
        "this trigger",
    ]

    query_heads = [
        "this query returns",
        "return",
        "returns",


        "a query that returns",
        "the query returns",


        "this query returns"
        "this query will return",
        "this querys returns",
        "this query lists",
        "this query searches",

        "query",

    ]
    action_heads = [
        "this action will",
        "the action will",
    ]

    head_words = []
    if mark == "trigger":
        head_words = trigger_heads
    if mark == "query":
        head_words = query_heads
    if mark == "action":
        head_words = action_heads

    if len(operations) == 0:
        return [], []

    new_operations = []
    params = set()
    for operation in operations:
        des = ' '.join(operation["description"].split()).lower()
        param = get_operation_parameters(operation, mark)
        for head in head_words:
            if des.startswith(head):
                des = des.replace(head, " ", 1)
                break
        new_operations.append(des)
        for ele in param:
            params.add(ele)
    return new_operations, params

def get_nn_from_api(operations, mark):
    edited_dess, params = preprocess_operations(operations, mark)
    pos = "pos"
    nn_words = set()
    if type(edited_dess) == type(None):
        return set()
    for des in edited_dess:
            sNLP = StanfordNLP()
            annotations = sNLP.annotate(des)["sentences"][0]
            # enhanced_dep = annotations["enhancedDependencies"]
            tokens = annotations["tokens"]

            potential_nn_index = []
            for tk in tokens:
                if tk[pos] in nn_marks:
                    potential_nn_index.append(True)
                else:
                    potential_nn_index.append(False)
            
            visited = [False] * len(tokens)
            
            
            for index in range(len(visited)):
                if visited[index] or potential_nn_index[index] == False:
                    continue
                
                ## find not visited nn words
                if potential_nn_index[index] == True:
                    tk = tokens[index]
                    str_nn = [tk["lemma"]]
                    visited[index] = True
                    for end in range(index + 1, len(visited)):
                        if potential_nn_index[end]:
                            str_nn.append(tokens[end]["lemma"])
                            visited[end] = True
                        else:
                            break
                    nn_words.add(' '.join(str_nn))

    return set(nn_words), params



def output_nn2json():
    #f = "/Users/***/Documents/Code/overclaim_tap/channel_api/cloud_storage_info.txt"
    f= "/Users/***/Documents/Code/overclaim_tap/oauth/channel_info_cleaned.txt"
    json_out_f = "/Users/***/Documents/Code/overclaim_tap/channel_api/channel_api_nn.txt"
    json_out_w = open(json_out_f, "w")

    ### pre process, assign value to channel_id_name dict
    load_channel_id_permission_log()
    
    lines = open(f, "r").readlines()
    verbs = []


    object_info = dict()
    for line in lines:
        channel = json.loads(line)["data"]["channel"]
        
        if type(channel) == type(None):
            continue
        channel_id = channel["id"]
        
        triggers = channel["triggers"]
        queries = channel["queries"]
        actions = channel["actions"]    

        triggers_nn, triggers_params = get_nn_from_api(triggers, "trigger")
        queries_nn, queries_params = get_nn_from_api(queries, "query")
        actions_nn, actions_params = get_nn_from_api(actions, "action")

        object_info["id"] = channel_id
        object_info["service_name"] = channel_id_name[channel_id]
        object_info["triggers_nn"] = list(triggers_nn)
        object_info["triggers_params"] = list(triggers_params)
        object_info["queries_nn"] = list(queries_nn)
        object_info["queries_params"] = list(queries_params)
        object_info["actions_nn"] = list(actions_nn)
        object_info["actions_params"] = list(actions_params)

        object_json = json.dumps(object_info)

        json_out_w.write(object_json + "\n")
        print(object_json)




if __name__ == "__main__":
    output_nn2json()