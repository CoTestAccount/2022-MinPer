from curses.ascii import isalpha
import os
import sys
import json
from nltk.corpus import wordnet
import nltk
nltk.download('punkt')

from permission_negative_ana import format_sentence
from permission_negative_ana import maybe_noise_for_grant_permission
from permission_negative_ana import pos_permissions, require_permissions, contains_neg_phrase
from permission_negative_ana import nlp

from tools import filter_lines_followed_agree

### import sentence parse tools standford_parser
sys.path.insert(1, "/Users/***/Documents/Code/overclaim_tap/stanford_parser")
import stanford_parser 
auth_folder = "/Users/***/Documents/Code/overclaim_tap/oauth/fetch_OAuth_info/auth_log/"
black_words_auth_log = [
    "",
]

debug_mode = False


verb_frequency = dict()
services_api_nn = dict()


def add_extra_sentence_require_permissions():
    file_path = "/Users/***/Documents/Code/overclaim_tap/oauth/permission_detail_ana/ask_for_require_permission_sentence.txt"
    lines = open(file_path, "r")
    for line in lines:
        nlp_permission = nlp(line.replace("\n", ""))
        global require_permissions
        require_permissions.append(nlp_permission)

def filter_sentence_question_mark(sentence):
    filtered_mark = ["password",
        "account",
        "new to",
        "sign up",
        "sign in",
        ]
    not_filtered_mark = [
        "grant",
        "ifttt",
        "this app",
        "the app",
    ]

    for filtered in filtered_mark: # filter out such sentence
        if filtered in sentence:
            return True
    
    for not_filtered in not_filtered_mark: # reserve such sentence
        if not_filtered in sentence:
            return False
    
    return True # filter such sentence

## get the corresponding relationship,  key is service/channel name (string)
##                                      value is noun array  ()
def load_permission_api_noun():
    api_noun_json_f = "/Users/***/Documents/Code/overclaim_tap/channel_api/channel_api_nn.txt"
    lines = open(api_noun_json_f, "r").readlines()

    
    for line in lines:
        nn_array = []
        object_json = json.loads(line)
        nn_array.extend(object_json["triggers_nn"])
        nn_array.extend(object_json["queries_nn"])
        nn_array.extend(object_json["actions_nn"])

        services_api_nn[object_json["service_name"]] = nn_array
    
    return services_api_nn

def require_permission_mark_sentence(lines):
    marks_index = set()
    for index, line in enumerate(lines):
        line =  format_sentence(line)
        if maybe_noise_for_grant_permission(line) or len(line.split(" ")) < 4:
            continue
        sentence = nlp(line)

        for pos_permission in pos_permissions:
            if pos_permission.similarity(sentence) > 0.9 and contains_neg_phrase(line) == False:
                marks_index.add(index)
                break

        for require_permission in require_permissions:
            if require_permission.similarity(sentence) > 0.9 and contains_neg_phrase(line) == False:
                marks_index.add(index)
                break
    return marks_index

def maybe_service_nn(candidates, nns):
    for candidate in candidates:
        if candidate in nns:
            return True
        
    for nn in nns:
        tks = nn.split(" ")
        if len(tks) > 1:
            for candidate in candidates:
                if candidate in tks:
                    return True
                try:
                    w1 = wordnet.synset('{}.n.01'.format(candidate))
                except:
                    continue


                for tk in tks:
                    try: 
                        w2 = wordnet.synset('{}.n.01'.format(tk))
                    except:
                        continue
                    if w1.wup_similarity(w2) > 0.9:
                        return True

    return False


def get_final_permission_range(ind_left_verb, ind_right_veb, index_permissions_set):
    if len(index_permissions_set) == 0:
        return ind_left_verb, ind_right_veb
    start = min(index_permissions_set)
    start = min(start, ind_left_verb)
    end = ind_right_veb
    for index in sorted(index_permissions_set):
        if index > end:
            end = index + 5

    return start, end


def remove_empty_line(lines):
    result = []
    for line in lines:
        letter_count = 0
        for s in line:
            if isalpha(s):
                letter_count += 1
        if letter_count < 3: ## contains only two letters, like ok/ eg/
            continue

        result.append(line)
    return result


def find_potantial_permission_info(lines, service_name):
    verbs = []
    index_maybe_permission = []

    print("################################")

    if service_name not in services_api_nn:
        print("cannot find permission nn key")
        return
    permission_nn = services_api_nn[service_name]
    lines = remove_empty_line(lines)

    for index,line in enumerate(lines):

        tks = line.split()
        if len(tks) < 3:
            continue
        if "?" in line and filter_sentence_question_mark(line):
            continue
        res, found = stanford_parser.preprocess_verb_noun_pair(line, service_name)

        if found == False:
            potential_nn = stanford_parser.parse_sentence_noun(line)
            potential_vebs, _ = stanford_parser.parse_sentence_veb(line)
            if maybe_service_nn(potential_nn, permission_nn) and len(potential_vebs) != 0:
                found = True
                print("##marked by nn: ", line)

        if found:
            index_maybe_permission.append(index)
    
    ## fetch range based on verb ana
    index_left, index_right = -1, -1
    if len(index_maybe_permission) > 0:
        index_right = index_maybe_permission[-1]
        index_left =  index_maybe_permission[0]

    ## fetch range based on require permission mark sentence ana
    require_permission_marks = require_permission_mark_sentence(lines)
    print("##find require permission mark sentence, begin to print,")
    for index in require_permission_marks:
        print(lines[index])
    print("##finish to print")
    index_left, index_right = get_final_permission_range(index_left, index_right, require_permission_marks)


    if index_left == -1 and index_right == -1:
        print("################################# cannot find permissions: " , service_name)
        return False

    
    sentences = lines[index_left: index_right+1]
    filtered_sentences = filter_lines_followed_agree(sentences)

    print("#################################" + " " + "potential permission: ", service_name)
    if len(filtered_sentences) > 0:
        print(''.join(filtered_sentences))
    else:
        print(''.join(sentences))

    return True




def process_auth_log_permission_lines():

    global services_api_nn, debug_mode
    services_api_nn = load_permission_api_noun()
    auth_files = os.listdir(auth_folder)
    
    selected = [
      #'Optoma', 'green_light_signal', 'bart_delay', 'putio', 'fiverr', 'xtactor', 'bocco_emo', 'bitmark', 'alpaca', 'app_store', 'invoxia_triby', 'isitchristmas', 'ohmconnect', 'itchio', 'Amba', 'patreon', 'lightwaverf_power', 'monzo', 'sesame', 'bocco', 'adafruit', 'dozens', 'publer', 'yelp', 'trakt', 'caavo', 'trigger_cmd', 'dominos', 'homelyenergy', 'sateraito_office', 'AlexaActionsByMkzense', 'pavlok', 'nj_transit', 'flic', 'glanceclock', 'hive_view', 'nano_lol', 'tochie_speaker', 'irobot', 'weara', 'electrolux', 'smarter', 'miyo', 'envoy', 'location', 'dol', 'google_assistant', 'tecan_connect', 'dondeesta', 'bea', 'unforgettable_me', 'atmoph', 'eggminder', 'alko_smart_garden', 'propublica', 'slickdeals', 'automower', 'nvd', 'hc_cook_processor', 'linkedin', 'fletti', 'zoom', 'maestro_by_stelpro', 'texas_legislature', 'epion', 'whisker',
        'onedrive', 'fiverr',
    ]
    for f in auth_files:
        path = auth_folder + f
        if "__phase1" in f:
            continue

        ###### to be deleted
        f_name = f.replace("_channels_","").replace("__phase2", "")
        if f_name not in selected and  debug_mode:
                continue
        #####
        lines = open(path, "r").readlines()
        found = find_potantial_permission_info(lines, f_name)


        ### try to find in phase1 file
        phase1_f = f.replace("phase2", "phase1")
        phase1_path = auth_folder + phase1_f
        if phase1_f in auth_files and found == False:
                lines = open(phase1_path, "r").readlines()
                found = find_potantial_permission_info(lines, f_name)



if __name__ == "__main__":
    debug_mode = False
    add_extra_sentence_require_permissions()
    process_auth_log_permission_lines()
