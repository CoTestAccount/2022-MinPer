## load permission info
def load_permission_info():
    permissions_lines = dict()
    f = '../dataset/atomic_result.txt'
    
    lines = open(f, "r").readlines()
    

    max_lines = len(lines)
    for i, line in enumerate(lines):
        if "# potential permission: " in line:
            ## find text info
            sentences = []
            service_name = line.replace("################################# potential permission:  ","").replace("\n","")
            for j in range(i+1, min(i+100,max_lines)):
                if "##################" in lines[j]:
                    break
                
                if lines[j] != '\n':
                    sentences.append(lines[j])
            permissions_lines[service_name] = sentences
    return permissions_lines

def is_verb_noise(line):
    blacklists = [
        'privacy policy', 'terms of service', 'privacy', 'policies',
        'username', 'email address',
        'log in', 'login',  'cookies',  'password', 'sign', 'please', 
        'agree', 'grant', 'consent', 'widget', ''
        '?', ':' ,'n\'t',  
        # 'account',
        ]
    for word in blacklists:
        if word in line:
            return True

    return False

def remove_empty_sent(lines):
    results = []
    for line in lines:
        if line == '\n':
            continue
        results.append(line)
    return results
            
def filter_verb_overclaim_noise(lines):
    filtered = []
    for line in lines:
        if is_verb_noise(line):
            continue
        filtered.append(line)
    filtered = remove_empty_sent(filtered)
    return filtered



def load_verb_overclaim(f):
    lines = open(f, 'r').readlines()

    service_name = ''
    overclaimed_p = []
    service_overclaimed = dict()

    countered = 0

    for line in lines:
        if 'remained oauth perms:' in line:
            service_name = line.replace(' remained oauth perms: \n', '')
            overclaimed_p = []
            countered = 0
            continue

        if '######' in line:

            if len(overclaimed_p) > 0 and service_name != '' and countered == 0:
                filtered = filter_verb_overclaim_noise(overclaimed_p)
                if len(filtered) > 0:
                    service_overclaimed[service_name] = filtered
                    # print('##########:', service_name)
                    # print(''.join(filtered))
            countered  = countered + 1
            overclaimed_p = []
            continue

        overclaimed_p.append(line)
        



    return service_overclaimed


def is_noun_noise(line, service_name):
    blacklist = [
        'access',  'device', 'service', 
        'ifttt', 'request', 'behalf', 'application', 'app', 'datum', 
         'permission', 'term', 'policy', 'email', 'party app', 
        # 'profile', 'information', 'setting', 'other'
        ]
    tks = line.split(' ##  ')
    noun = tks[len(tks) - 1]

    for word in blacklist:
        if word in noun:
            return True
    
    # tks = noun.split(' ')
    # for tk in tks:
    #     tk = tk.replace('\n', '')
    #     if tk != '' and tk in service_name:
    #         return True

    return False

def filter_noun_overclaim_noise(lines, service_name):
    filtered_1 = filter_verb_overclaim_noise(lines)
    filtered_2 = []
    for line in filtered_1:
        if is_noun_noise(line, service_name):
            continue
        filtered_2.append(line)
    filtered_2 = remove_empty_sent(filtered_2)
    return filtered_2



def load_noun_overclaim(f):
    lines = open(f, 'r').readlines()
    service_overclaimed_p = dict()
    service_name = ''
    perms = []

    whole_text_length = len(lines)
    
    i = 0
    
    while i <  whole_text_length:
        line = lines[i]
        if 'begin to detect nn overclaim:' in line:
            service_name = line.replace('begin to detect nn overclaim:  ', '').replace('\n', '')

        if '## found nn overclaim in sentence:' in line:
            noun = line.replace('## found nn overclaim in sentence:', '').replace('\n', '')
            modified = lines[i+1].replace('\n', '') + ' ## ' + noun + '\n' 
            perms.append(modified)
            i = i + 2
            continue

        if '#######################################' in line:
            i = i + 1
            continue

        if '###################' in line:
            if len(perms) > 0 and len(service_name) > 0 :
                filtered = filter_noun_overclaim_noise(perms, service_name)
                if len(filtered) > 0:
                    service_overclaimed_p[service_name] = filtered
                    # print('#######:', service_name)
                    # print(''.join(filtered))

            perms = []
        
        i = i + 1
    
    if len(perms) > 0:
                filtered = filter_noun_overclaim_noise(perms, service_name)
                if len(filtered) > 0:
                    service_overclaimed_p[service_name] = filtered
                    # print('#######:', service_name)
                    # print(''.join(filtered))
                    
    return service_overclaimed_p


## the following two functions are just a copy of same functiom in overclaim detection for verb
def preprocess_atomic_permission(line):
    line =  line.replace('\n', '')
    special_cases = {
        '-LRB-': '(',
        '-RRB-': ')',
    }

    for case in special_cases:
        line = line.replace(case, special_cases[case])
    return line

def load_atomic_permission(f):
    file = '../dataset/atomic_result.txt'
    if f != '':
        file = f

    lines = open(file, 'r').readlines()
    service_atomatic_permissions = dict()
    permissions  = []
    service_name = ''
    for line in lines:
        if 'service name: ' in line:
            service_atomatic_permissions[service_name] = permissions
            service_name = line.replace('service name:  ', '').replace('\n', '')
            permissions = []
            continue
        if '#########' in line:
            continue
        
        permissions.append(preprocess_atomic_permission(line))
    
    if len(permissions) > 0:
        service_atomatic_permissions[service_name] = permissions
    return service_atomatic_permissions