
from __future__ import annotations
import json
import sys
sys.path.insert(1, "/Users/***/Documents/Code/overclaim_tap/stanford_parser")
from stanford_parser import sent_annotation
from stanford_parser import parse_sentence_veb
from atomic_operation import parse_sentence_verb_obj_pair, parse_sentence_obl, capture_core_kernel_noun
sys.path.insert(1, "/Users/***/Documents/Code/overclaim_tap/nn_overclaim")
from nn_overclaim_det import is_nn_similarity
from verb_group import get_channel_id_name
sys.path.insert(1, '/Users/***/Documents/Code/overclaim_tap/side_tools')
from fetch_benchmark_seed import fetch_seed_benchmark
from load_finfo import load_atomic_permission

verb_strict_similar_words = dict()
verb_loose_similar_words = dict()
channel_id_name = dict()
manual_fix_verb_group = { ## 1 means create a not existing items, 2 means modify already existing items
    'add':      {'1': 'create',     '2': 'modify'},
    'upload':   {'1':'create',      '2': ''},
    'append':   {'1': 'create',     '2': 'modify'},
    'access':   {'1': 'read',       '2': 'read'},
    'identify': {'1':'read',        '2':'read'},
}


general_verbs = ['control', 'manage', 'use']
general_nouns = ['devices', 'device', 'appliances', 'appliance', 'services',]

general_verb_noun_pairs = [('send', 'command')]

api_trigger_query_des, api_action_des = dict(), dict()
debug_mode = False
test_service_names = []
benchmark_mode = False


def process_multiple_verb_oauth(sentence):
    annotations = sent_annotation(sentence)["sentences"][0]
    tokens = annotations["tokens"]

    unchanged = False
    pos_to_index, pos_ifttt_index  = -1, -1

    for ind, tk in enumerate(tokens):
        if pos_to_index > -1:
            break

        if tk['lemma'] == 'allow' and tk['pos'] != 'VBN':
            ### first -> find 'to'
            for j in range(ind +1, len(tokens)):
                if tokens[j]['lemma'] == 'to':
                    pos_to_index = j
                    break
                if tokens[j]['lemma'] == 'ifttt':
                    pos_ifttt_index = j

        if tk['lemma'] == 'allow' and tk['pos'] == 'VBN':
            unchanged = True

    pos_index = -1
    if pos_to_index > -1:
        pos_index = pos_to_index
    elif pos_ifttt_index > -1:
        pos_index = pos_ifttt_index

    if unchanged:
        return sentence

    if pos_index == -1 and unchanged == False:
        return ''

    result_tk = []
    for ind in range(pos_index + 1, len(tokens)):
        result_tk.append(tokens[ind]['word'])
    return ' '.join(result_tk)




def manual_fix_verb(api_des, service_name, verb, noun):
    global manual_fix_verb_group, debug_mode
    obl = parse_sentence_obl(api_des)

    if obl == '' or is_nn_similarity(service_name, obl):
        return (manual_fix_verb_group[verb]['1'], noun)
    else:
        return (manual_fix_verb_group[verb]['2'], obl)



def indexing_api_pairs(api_permissions, service_name):
    global debug_mode

    manual_fix_info = []
    original_info = []
    for api_perm in api_permissions:
        api_pairs = parse_sentence_verb_obj_pair(api_perm)
        for pair in api_pairs:
            if pair[0].lower() in manual_fix_verb_group:
                #api_contains_manual_verb_group = True
                replace_verb, replace_noun = manual_fix_verb(api_perm, service_name, (pair[0]).lower(), pair[1])
                if debug_mode:
                    print('manual fix api_pairs: ', pair, 'to: (', replace_verb, replace_noun, ')')
                manual_fix_info.append((replace_verb, replace_noun))
            original_info.append(pair)
    
    return original_info, manual_fix_info 


def remove_header(des):
    action_heads = [
        "this action will",
        "the action will",
    ]

    content = des.lower()
    for head in  action_heads:
        content = content.replace(head, '')
    return content

def load_api_descripiton():
    global channel_id_name

    global debug_mode, test_service_names

    file_channel = '/Users/***/Documents/Code/overclaim_tap/oauth/channel_info_cleaned.txt'
    
    lines = open(file_channel, 'r').readlines()

    services_actions_des = dict()
    services_triggers_queries_des = dict()


    for line in lines:
        obj = json.loads(line)
        channel = obj['data']['channel']
        triggers,queries,actions = channel['triggers'], channel['queries'], channel['actions']


        c_id = channel['id']
        c_name = channel_id_name[c_id]

        if triggers == None and queries == None:
            continue
        

        ## begin to process triggers  and queries
        services_triggers_queries_des[c_name] = []

        if actions == None:
            continue
        

        if (debug_mode or benchmark_mode) and (c_name not in test_service_names):
            continue

        services_actions_des[c_name] = []
        

        #services_actions_fields[] = []
        for action in actions:
            action_name = action['name']

            pairs = parse_sentence_verb_obj_pair(action_name)
            if len(pairs) > 0:
                services_actions_des[c_name].append(action_name)
                continue

            ## if information in name is not enough, we would use the description name
            des = remove_header(action['description'])
            services_actions_des[c_name].append(des)
            # for field in  action_fields:
    
    return services_actions_des, services_triggers_queries_des

def is_non_read_verb(verb):
    global debug_mode

    black_lists = ['make', 'manage']
    seed_verb = ['read', 'see', 'view']
    if verb in black_lists:
        return True
    #unsimilar_count = 0
    for seed in  seed_verb:
        if similar_operaor(seed, verb) == True:
            if debug_mode:
                print('read similar verb: ', verb)
            return False
    return True


def process_no_action(oauth_permissions):
    verbs = []
    indexs = []
    for ind, perm in enumerate(oauth_permissions):
        pairs  = parse_sentence_verb_obj_pair(perm)
        if len(pairs) == 1:
            verbs.append(pairs[0][0])
            indexs.append(ind)
    
    #verbs = list(set(verbs))
    result = []
    for ind,verb in enumerate(verbs):
            if is_non_read_verb(verb):
                result.append(oauth_permissions[ind])
    return result

def load_verb_group():
    file = '/Users/***/Documents/Code/overclaim_tap/verb_overclaim/verb_cluster.txt'
    lines = open(file, 'r').readlines()

    verb_strict_similar_words = dict()
    verb_loose_similar_words = dict()

    for line in lines:
        tokens = line.replace('\n', '').split('\t')
        if len(tokens) != 3:
            continue
        verb = tokens[0]
        strict_similar = tokens[1].replace('strict: ', '').split(',')
        loose_similar = tokens[2].replace('loose: ', '').split(',')

        verb_strict_similar_words[verb] = strict_similar
        verb_loose_similar_words[verb] = loose_similar
    return verb_strict_similar_words, verb_loose_similar_words
    
def similar_operaor(verb_api, verb_oauth):
    global verb_strict_similar_words, verb_loose_similar_words
    blacklist = ['make', 'manage']
    if verb_api != verb_oauth and (verb_api in blacklist or verb_oauth in blacklist):
        return False

    if verb_api == verb_oauth:
        return True


    ## first step
    if verb_api not in verb_loose_similar_words or verb_oauth not in verb_loose_similar_words:
        return False

    if verb_api in verb_loose_similar_words[verb_oauth] or verb_oauth in verb_loose_similar_words[verb_api]:
        return True

    # second step, can be connect by 2 loops
    strict_oauth = verb_strict_similar_words[verb_oauth]
    strict_api = verb_strict_similar_words[verb_api]

    intersec = list(set(strict_api) & set(strict_oauth))
    if len(intersec) > 0:
        return True
 

    # for middle_v in strict_oauth:
    #     if middle_v == '':
    #         continue
    #     m_sims = verb_strict_similar_words[middle_v]
    #     for m_sim in m_sims:
    #         if m_sim in strict_api:
    #             return True

    # for middle_v in strict_api:
    #     if middle_v == '':
    #         continue
    #     m_sims = verb_strict_similar_words[middle_v]
    #     for m_sim in m_sims:
    #         if m_sim in strict_oauth:
    #             return True

    return False

def similar_operand(noun_api, noun_oauth):

    global debug_mode
    if debug_mode == True:
        print('service api noun: ', noun_api, 'oauth noun: ', noun_oauth )


    if noun_api in noun_oauth or noun_oauth in noun_api:
        return True
    
    sim_ori = is_nn_similarity(noun_api, noun_oauth)
    
    if sim_ori:
        return True


    core_noun_api = capture_core_kernel_noun(noun_api)
    core_noun_oauth = capture_core_kernel_noun(noun_oauth)


    if debug_mode:
        print('core nn: ', core_noun_api, core_noun_oauth)

    if core_noun_api in core_noun_oauth or core_noun_oauth in core_noun_api:
        return True
    
    sim_core = is_nn_similarity(core_noun_api, core_noun_oauth)
    return sim_core
    
    # tks_api = noun_api.split(' ')
    # tks_oauth = noun_api.split(' ')

    # count = 0
    # for tk in tks_api:
    #     if tk in tks_oauth:
    #         count += 1

    # if count * 1.0 / min(len(tks_oauth), len(tks_api)) * 1.0 > 0.5:
    #     return True

    # return False


def similar_general_noun(oauth_obj):
    for noun in general_nouns:
        if noun in oauth_obj:
            return True
    return False


def similar_general_pairs(oauth_verb, oauth_obj):
    for pair in general_verb_noun_pairs:
        if oauth_verb == pair[0] and oauth_obj == pair[1]:
            return True
    return False

def similar_operator_operand(api_pair, oauth_pairs):

    #debug_mode = True
    ## debug mode
    global debug_mode
    if debug_mode == True:
        print('in similar operator and operand function: ',  'oauth_pairs: ', oauth_pairs, 'api_pairs: ', api_pair)
    
    if api_pair == None or oauth_pairs == None:
        return False
        
    if len(oauth_pairs) == 0:
        return False

    oauth_v = oauth_pairs[0][0]
    oauth_obj = oauth_pairs[0][1]


    Found = False
    
    if debug_mode and similar_operand(api_pair[1], oauth_obj):
        print('sim obj: ', api_pair[1], oauth_obj)

    if similar_operaor(api_pair[0], oauth_v) and similar_operand(api_pair[1], oauth_obj):
            print('similar: verb ', api_pair[0], oauth_v, ' obj: ', api_pair[1], oauth_obj)
            return True

    if oauth_v in general_verbs and similar_operand(api_pair[1], oauth_obj):
        print('similar: verb ', api_pair[0], oauth_v, ' obj: ', api_pair[1], oauth_obj)
        return True

    if similar_operaor(api_pair[0], oauth_v) and similar_general_noun(oauth_obj):
        print('similar: verb ', api_pair[0], oauth_v, ' obj: ', api_pair[1], oauth_obj)
        return True

    if oauth_v in general_verbs and similar_general_noun(oauth_obj):
        print('similar: verb ', api_pair[0], oauth_v, ' obj: ', api_pair[1], oauth_obj)
        return True

    if similar_general_pairs(oauth_v, oauth_obj):
        print('similar: verb ', 'general pairs', oauth_v, ' obj: ', 'general paris', oauth_obj)
        return True
    return False


def find_cloest_api_permission(oauth_perm,api_pairs, manual_pairs ,service_name):
    oauth_pairs = parse_sentence_verb_obj_pair(oauth_perm)
    
    if len(oauth_pairs) == 0:
        print('unable to parse the verb and noun pair for oauth perms:', oauth_perm)
    if len(oauth_pairs) > 1:
        print('oauth permission has more than one permission: ', oauth_pairs)
        verbs = []
        for pair in oauth_pairs:
            verbs.append(pair[0])
        if 'allow' in verbs:
            oauth_perm = process_multiple_verb_oauth(oauth_perm)
            oauth_pairs = parse_sentence_verb_obj_pair(oauth_perm)

    for api_pair in api_pairs:
        if similar_operator_operand(api_pair, oauth_pairs):
            print('find corresponding perm', oauth_pairs, '#####', api_pair)
            return True

    for manual_pair in manual_pairs:
        if similar_operator_operand(manual_pair, oauth_pairs):
            print('find corresponding perm based on manual fix', oauth_pairs, '#####', manual_pair)
            return True


    return False



def process_has_action(oauth_permissions, api_permissions, manual_pairs ,service_name):
    ## if operation doesn't belong to the same group
    global debug_mode
    read_remained = []
    remained = []
    for perm in oauth_permissions:
        if perm == None or len(perm) == 0:
            continue

        pairs = parse_sentence_verb_obj_pair(perm)
        
        if debug_mode:
            print('oauth pairs: ', pairs, 'sentences: ', perm)
        if len(pairs) == 0:
            continue

        verb = pairs[0][0]
        if is_non_read_verb(verb):
            remained.append(perm)
        else:
            read_remained.append(perm)

    new_remained = []
    for perm in remained:
        found_array = find_cloest_api_permission(perm, api_permissions, manual_pairs, service_name)
        if found_array == False:
            new_remained.append(perm)
    
    if debug_mode:
        print('remained action perm:', new_remained)
        print('remained read perm:', read_remained)
        print('original perms:', oauth_permissions)
    
    return new_remained, read_remained # remained is usually redudant


def test_similar_word(w1, w2):
    # w1 = 'see'
    # w2 = 'delete'
    if similar_operaor(w1, w2):
        print('similar')

    global verb_strict_similar_words, verb_loose_similar_words

    print(verb_loose_similar_words[w1], verb_loose_similar_words[w2])




def format_print_remained_perm(remained, service):
    print('#################')
    print(service, 'remained oauth perms: ')
    for perm in remained:
                perm_pairs = parse_sentence_verb_obj_pair(perm)
                addi_info = ''
                for pair in perm_pairs:
                    if len(pair) != 2:
                        continue
                    addi_info = addi_info + pair[0] + ', ' + pair[1] + '|'
                print(perm, '||||', addi_info)
    print('##############')
    return

def test_overclaim_verb():

    global test_service_names, debug_mode, benchmark_mode
    global atomatic_oauth
    global api_trigger_query_des, api_action_des
    global verb_strict_similar_words, verb_loose_similar_words, channel_id_name

    for service in atomatic_oauth:
        if (debug_mode or benchmark_mode) and service not in test_service_names:
            continue

        oauth_permissions = atomatic_oauth[service]
        if service not in api_action_des and service in api_trigger_query_des:
            remained = process_no_action(oauth_permissions)
            format_print_remained_perm(remained, service)

        if service in api_action_des and service in api_trigger_query_des:
            api_pairs, manual_pairs = indexing_api_pairs(api_action_des[service], service)
            remained, _ = process_has_action(oauth_permissions, api_pairs, manual_pairs ,service)
            format_print_remained_perm(remained, service)

        if service in api_action_des and service not in api_trigger_query_des:
            api_pairs, manual_pairs = indexing_api_pairs(api_action_des[service], service)
            _, remained = process_has_action(oauth_permissions, api_pairs, manual_pairs,service)
            format_print_remained_perm(remained, service)



if __name__ == '__main__':
    debug_mode = False
    #benchmark_mode = True
    benchmark_mode = False
    #test_service_names = ['twitch']
    test_service_names = fetch_seed_benchmark()


    
    verb_strict_similar_words, verb_loose_similar_words = load_verb_group()
    channel_id_name = get_channel_id_name()
    api_action_des, api_trigger_query_des = load_api_descripiton()

    atomic_f = '/Users/***/Documents/Code/overclaim_tap/stanford_parser/analysis/atomic_result_v2.txt'
    if benchmark_mode:
        atomic_f = '/Users/***/Documents/Code/overclaim_tap/stanford_parser/analysis/benchmark_atomic_result_v2.txt'
    atomatic_oauth = load_atomic_permission(atomic_f)
    
    test_overclaim_verb()

    # test_similar_word('add', 'create')
    # sent = 'add a new item to your Pocket queue'
    # manual_fix_verb(sent, '')

    
