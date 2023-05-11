import sys
import json

from nltk.stem import WordNetLemmatizer

sys.path.insert(1, "../stanford_parser")
from stanford_parser import preprocess_verb_noun_pair, parse_sentence_veb ,parse_sentence_noun
from atomic_operation import parse_sentence_verb_obj_pair
from nltk.corpus import wordnet

from load_finfo import load_atomic_permission

lemmatizer = WordNetLemmatizer()
black_list_nouns = ['application', 'ifttt', 'account']
debug_mode, benchmark_mode = False, False



## load operation info
def load_operation_nn():
    services_api_nn = dict()
    path = "../dataset/channel_api_nn.txt"
    lines = open(path, "r")
    for line in lines:
        nn_array = []
        object_json = json.loads(line)
        nn_array.extend(object_json["triggers_nn"])
        nn_array.extend(object_json["queries_nn"])
        nn_array.extend(object_json["actions_nn"])

        nn_array.extend(object_json["triggers_params"])
        nn_array.extend(object_json["queries_params"])
        nn_array.extend(object_json["actions_params"])

        services_api_nn[object_json["service_name"]] = nn_array
    
    return services_api_nn

def word_similarity(nn1, nn2):
    try: 
        w1 = wordnet.synset('{}.n.01'.format(nn1))
    except:
        return False
    try:
        w2 = wordnet.synset('{}.n.01'.format(nn2))
    except:
        return False
    #print(nn1, nn2, "similarity: ", w1.wup_similarity(w2))
    if w1.wup_similarity(w2) > 0.8:
        return True
    return False


def remove_same_prefix(tks1,tks2):
    flag = -1
    for i in range(0, min(len(tks1), len(tks2))):
        if tks1[i] == tks2[i]:
            continue
        else:
            flag = i
            break
    if flag > 0:
        return tks1[flag:], tks2[flag:]
    return tks1, tks2

def phrase_similarity(nn1, nn2):
    tks1 = nn1.split()
    tks2 = nn2.split()


    ## eg: email address v.s. email
    ## zoom meeting v.s. meeting
    ## user picture v.s. display picture

    if nn1 in nn2 or nn2 in nn1:
        return True

    if debug_mode:
        print('tks1:', tks1, 'tks2:', tks2)
    count = 0

    # tks1, tks2 = remove_same_prefix(tks1, tks2)
    # if debug_mode:
    #     print('removed tks1:', tks1, 'tks2:', tks2)
    bad_case = ['account']

    if tks1[-1] in bad_case and tks2[-1] not in bad_case:
        return False
    if tks2[-1] in bad_case and tks1[-1] not in bad_case:
        return False

    for tk in tks1:
        if tk in tks2:
            count = count + 1
    
    length = min(len(tks1), len(tks2))
    if count >= 1 and count* 1.0 / length * 1.0 > 0.48:
        return True
    return False

def is_nn_sim_bad_case(nn1, nn2):
    if len(nn1.split(' ')) > 1 or len(nn2.split(' ')) > 1:
        return False 

    bad_cases = [
        ('photo','video'),
        ('picture', 'video'),
    ]


    nn1_lemma = lemmatizer.lemmatize(nn1)
    nn2_lemma = lemmatizer.lemmatize(nn2)
    for bc in bad_cases:
        if nn1_lemma == bc[0] and nn2_lemma == bc[1]:
            return True
        if nn2_lemma == bc[0] and nn1_lemma == bc[1]:
            return True
    return False

def is_nn_similarity(nn1,nn2):
    ## first round, consider all the noun 
    global debug_mode
    synonyms_1, synonyms_2 = [], []

    if is_nn_sim_bad_case(nn1, nn2):
        return False ## not similar


    for syn in wordnet.synsets(nn1):
        for l in syn.lemmas():
            synonyms_1.append(l.name())
    
    for syn in wordnet.synsets(nn2):
        for l in syn.lemmas():
            synonyms_2.append(l.name())
    

    for w1 in synonyms_1:
        for w2 in synonyms_2:
            if word_similarity(w1, w2) > 0.8:
                if debug_mode:
                    print(w1, w2, "similarity")
                return True
    

    if nn1 in synonyms_2 or nn2 in synonyms_1:
        if debug_mode:
            print('nn1 or nn2 is in synonym set: ', nn1, nn2)
        return True
    
    if debug_mode:
        print('begin to detect phrase similarity:', nn1, nn2)

    if phrase_similarity(nn1, nn2):
        return True

    return False


def preprocess_sentence(permission):
    global debug_mode
    verb_obj_pairs = parse_sentence_verb_obj_pair(permission)
    if debug_mode:
        print('verb obj pairs:', verb_obj_pairs)

    nn_permissions = []
    if len(verb_obj_pairs) == 0:
        verbs, potential = parse_sentence_veb(permission)
        if len(verbs) == 0:
            nn_permissions  = parse_sentence_noun(permission)

            if debug_mode:
                print(permission)
                print('no verb, nn in permission', nn_permissions)
    
    bad_cases_v = [
        'display'
    ]
    bad_cases_n = [
        'name',
        'picture',
        'contacts', 'contact',
        'friends', 'friend',

    ]

    if len(verb_obj_pairs) > 0:
        for pair in verb_obj_pairs:
            
            verb, obj = pair[0], pair[1]
            if verb in bad_cases_v and obj in bad_cases_n:
                nn_permissions.append('displayed ' + obj)
            else:
                nn_permissions.extend(parse_sentence_noun(obj))


    if debug_mode:
        print('nn permissions:', nn_permissions)
    return nn_permissions



## use stanford parse to find the actual nn related with permission
def detect_nn_overclaim(permissions, service_operation_nns, service_name):
    global debug_mode
    print("###################\nbegin to detect nn overclaim: ", service_name)
    if debug_mode:
        print('permission:', permissions)
    for permission in permissions:
        # cutted_sentences, is_permission = preprocess_verb_noun_pair(permission, service_name)
        # if is_permission == False:
        #     continue

        nn_permissions = preprocess_sentence(permission)

        if debug_mode:
            print('permission:', permission, 'nn in permission:', nn_permissions)

        for nn_per in nn_permissions:
                if nn_per in service_operation_nns:
                    continue
                exist_sim_words = False
                for nn_operation in service_operation_nns:
                    if is_nn_similarity(nn_per, nn_operation):
                        if debug_mode:
                            print('find similar operation nn:', nn_operation, nn_per)
                        exist_sim_words = True
                        break
                for word in black_list_nouns:
                    if word in nn_per:
                        exist_sim_words = True
                        
                if exist_sim_words == False:
                    print("## found nn overclaim in sentence: ", nn_per)
                    print(permission)




## extract information and it's attribute from services operation parameter





if __name__ == "__main__":
    # debug_mode = True
    # benchmark_mode = True
    ### need to start stanford parse
    operations_nn = load_operation_nn()


    atomic_f = '../dataset/atomic_result.txt'
    permission_info = load_atomic_permission(atomic_f)


    selected = []
    for service_name in operations_nn:
         if service_name not in permission_info:
            continue

         if (debug_mode or benchmark_mode) and (service_name not in selected):
            continue

         detect_nn_overclaim(permissions=permission_info[service_name], service_operation_nns=operations_nn[service_name], service_name=service_name)

