from curses.ascii import isalpha, isdigit
from distutils.log import error
from tabnanny import check
from enchant.checker import SpellChecker
import shutil
from langdetect import detect
import json
import os
import string

from nltk.tokenize import sent_tokenize

#auth_folder = "/Users/***/Documents/Code/overclaim_tap/oauth/fetch_OAuth_info/auth_log/"
auth_folder = "/Users/***/Documents/Code/overclaim_tap/database/oauth_backup/auth_log/"
empty_auth = "/Users/***/Documents/Code/overclaim_tap/oauth/empty_auth/"
no_english_auth = "/Users/***/Documents/Code/overclaim_tap/oauth/no_english_auth/"
no_info_auth = "/Users/***/Documents/Code/overclaim_tap/oauth/no_info_auth/"
channel_api_file="/Users/***/Documents/Code/overclaim_tap/oauth/services_channel_info.txt"
channel_api_remove_noise_file="/Users/***/Documents/Code/overclaim_tap/oauth/channel_info_cleaned.txt"
modified_auth_folder= "/Users/***/Documents/Code/overclaim_tap/oauth/fetch_OAuth_info/modified_auth_log/"

mark_1 = ["Get access to 20 Applets, multiple actions, and other advanced features.", "Start 7-day trial"]
special_characters = ['©']


def is_empty_file(file):
    if os.stat(file).st_size == 0:
        return True
    return False

def is_no_auth_file(file): # direcely back to ifttt applets page, no auth info appears
    lines = open(file, "r").readlines()

    text = ' '.join(lines)
    if mark_1[0] in text and mark_1[1] in text:
        return True
    
    return False


def is_no_english_text(text):
    try:
        re = detect(text)
    except:
        #print("################")
        #print("throw a error:", text)
        return True
    if re != "en":
        #print("##########################")
        #print(text)
        return True
    return False

def process_oauth_noise():
    files = os.listdir(auth_folder)
    for file in files:
        if file == "backup":
            continue

        path = auth_folder + file

        # if is_no_auth_file(path):
        #     shutil.move(path, no_info_auth + file)
        #     continue

        # if is_no_english_file(path):
        #     shutil.move(path, no_english_auth + file)
        #     continue




def get_tri_que_act_description(api_list):
    descs = []
    for api in api_list:
        descs.append(api['name'])
        descs.append(api["description"])
    return ' '.join(descs)


def is_no_english_api_call(channel):
    descrition = channel["description"]

    tri_des = get_tri_que_act_description(channel["triggers"])
    que_des = get_tri_que_act_description(channel["queries"])
    act_des = get_tri_que_act_description(channel["actions"])

    text = descrition + ' ' + tri_des + ' ' + que_des + ' ' + act_des + ' '
    if is_no_english_text(text):
        return text, True
    
    return text, False



def process_channel_api_noise(channel_api_file):
    lines = open(channel_api_file, "r").readlines()
    f_out = open(channel_api_remove_noise_file, "w")

    for line in lines:
        if line == '\n':
            continue
        obj = json.loads(line)
        channel = obj["data"]["channel"]
        if type(channel) == type(None):
            print("#######################")
            print("empty channel: ", line)
            continue
        text, found = is_no_english_api_call(channel)
        if found:
            print("#####################")
            print("no english text channel: ", text)
            continue
        f_out.write(line)




### main function

def remove_special_characters(text):
    if '©' in text:
        text = text.replace('©', '')
        text.strip()
    return text

def is_no_alpha_text(text):
    for s in text:
        if isalpha(s):
            return False
    return True

def modify_list_mark(text):
    if len(text) >= 2 and isdigit(text[0]) and text[1] == '.':
        text = text[0] + ',' + text[2:]
    return text

def sentence_split(file):
    path = auth_folder + file
    lines = open(path, 'r').readlines()

    sentences = []
    for line in lines:
        ## remove line with empty letter
        if is_no_alpha_text(line):
            continue
        ## preprocess line
        line = modify_list_mark(remove_special_characters(line))

        sent_tks = sent_tokenize(line)
        sentences.extend(sent_tks)
    
    return sentences

def write_new_file(file):
    new_file = modified_auth_folder + file
    f = open(new_file, 'w')
    sentences = sentence_split(file)
    print("#########################")
    print(file)
    print(sentences)
    for line in sentences:
                f.write(line)
                f.write("\n")
    f.close()


if __name__ == "__main__":
    # files = os.listdir(auth_folder)
    # for file in files:
    #     write_new_file(file)
    process_channel_api_noise(channel_api_file)



        

