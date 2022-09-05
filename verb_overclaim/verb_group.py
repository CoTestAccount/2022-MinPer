import json
import sys 
sys.path.insert(1, "/Users/***/Documents/Code/overclaim_tap/nn_overclaim")
from nn_frequency import load_services_group
from nn_overclaim_det import load_permission_info
sys.path.insert(1, "/Users/***/Documents/Code/overclaim_tap/stanford_parser")
from stanford_parser import parse_sentence_veb
from oxford_dictionary import word_api_call




def get_channel_id_name():
    path = '/Users/***/Documents/Code/overclaim_tap/database/channel_id_name.txt'
    lines = open(path, "r")
    id_name = dict()
    for line in lines:
        tks = line.replace('\n', '').split(' ')
        if len(tks) < 2:
            continue
        id_name[tks[0]] = tks[len(tks) - 1]
    return id_name

def get_service_api_verb():
    file_path = '/Users/***/Documents/Code/overclaim_tap/database/'
    lines = open(file_path, "r").readlines()
    id_name = get_channel_id_name()

    all_verbs = set()
    services_actions = dict()
    for line in lines:
        json_obj = json.loads(line)['data']['channel']
        #service_name = json_obj['name']
        service_name = id_name[json_obj['id']]
        actions = json_obj['actions']

        actions_verbs = []
        for action in actions:
            #name = action['name']
            description = action['description']
            verb, potential = parse_sentence_veb(description)
            actions_verbs.extend(verb)
        
        services_actions[service_name] = actions_verbs
        all_verbs.update(actions_verbs)
    return services_actions, all_verbs

def get_oauth_verbs():
    service_permissions = load_permission_info()
    service_oauth_verbs = dict()

    all_verbs = set()
    for service in service_permissions:
        permissions = service_permissions[service]

        oauth_verbs = []
        for permission in permissions:
            verbs, potential = parse_sentence_veb(permission)
            oauth_verbs.extend(verbs)
        service_oauth_verbs[service] = oauth_verbs
        all_verbs.update(oauth_verbs)

    return service_oauth_verbs, all_verbs


def compare_verb_oauth_service():
    service_oauth_verb = get_oauth_verbs()

    service_action_name = get_service_api_verb()
    service_action_verb = dict()
    for service in service_action_name:
        actions_name = service_action_name[service]
        actions_verb = []
        for action in actions_name:
            tks = action.split(' ')
            actions_verb.append(tks[0])
        service_action_verb[service] = actions_verb

    for service in service_action_verb:
        print("############### ", service)
        print("action verbs: ", service_action_verb[service])

        if service in service_oauth_verb:
            print("oauth verbs: ", service_oauth_verb[service])

def opposite_meanning(verb1, verb2, opposite_words):
    if verb1 in opposite_words[verb2] or verb2 in opposite_words[verb1]:
        return True
    return False
       
def two_verb_same_group(verb1, verb2, similar_words, opposite_words, constraint):

    if verb1 in opposite_words[verb2] or verb2 in opposite_words[verb1]:
        return False

    if constraint == 'loose'  and (verb1 in similar_words[verb2] or verb2 in similar_words[verb1]):
        return True
    
    if constraint == 'strict' and (verb1 in similar_words[verb2] and verb2 in similar_words[verb1]):
        return True

    return False
    # return False
    
    # sim1 = similar_words[verb1]
    # sim2 = similar_words[verb2]

    # if len(sim2) == 0 or len(sim1) == 0:
    #     return False

    # return (not set(sim1).isdisjoint(sim2))

def load_verb_sim_oop():
    file = '/Users/***/Documents/Code/overclaim_tap/verb_overclaim/verb_sim_opp.txt'
    lines = open(file, 'r').readlines()
    verb_similar_words = dict()
    verb_opposite_words = dict()


    all_verbs = []
    for line in lines:
        tks = line.replace('\n', '').split('\t')
        if len(tks) < 3:
            continue
        verb = tks[0]
        all_verbs.append(verb)
        verb_similar_words[verb] = tks[1].split(',')
        verb_opposite_words[verb] = tks[2].split(',')

    return all_verbs, verb_similar_words, verb_opposite_words


def expansion(ori, remains, verb_similar_words ,verb_opposite_words, constraint):
    groups = []

    for ele in remains:
            if ele == ori:
                continue
            
            if opposite_meanning(ori, ele, verb_opposite_words):
                    continue

            if two_verb_same_group(ori, ele, verb_similar_words, verb_opposite_words, constraint):
                        groups.append(ele)
    return groups


def group_verb_based_oxford_dictionary(verbs):

    ## one priciple, verb that has opposite meanning should never appear in the same cluster
    # clusters = []
    # for verb in verbs:
    #     similar, opposite = word_api_call(verb)
    #     ## at the beginning, each words is a cluster -> then merge them

    #     print(verb + '\t' + ','.join(similar) + '\t' + ','.join(opposite))
    
    # ## begin to merge two cluster

    all_verbs, verb_similar_words, verb_opposite_words = load_verb_sim_oop()

    original_cluster = dict()
    for ele in all_verbs:
        group_strict = expansion(ele, all_verbs, verb_similar_words, verb_opposite_words, 'strict')
        group_loose = expansion(ele, all_verbs, verb_similar_words, verb_opposite_words, 'loose')

        print(ele + '\t' + 'strict: ' + ','.join(group_strict) + '\t' + 'loose: ' + ','.join(group_loose))

    

    # for key in original_cluster:
    #     groups = original_cluster[key]
        
    #     cluster = groups
    #     print('####')
    #     for ele in groups:
    #         if ele in original_cluster:
    #             cluster.extend(original_cluster[ele])
    #     print('ele: ', key, 'cluster: ', set(cluster))

        





def load_all_verbs():
    file = '/Users/***/Documents/Code/overclaim_tap/verb_overclaim/oauth_service_verbs.txt'
    lines = open(file, 'r').readlines()
    words = [line.strip('\n') for line in lines]
    result = [word for word in words if '#' not in word]
    return list(set(result))

if __name__ == '__main__':
    # all_verbs = load_all_verbs()
    merged = group_verb_based_oxford_dictionary([])
    # for cluster in merged:
    #     print("cluster: ", cluster)

   
        






