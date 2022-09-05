

mark_include_sentence = ['This includes the following:']
def contain_include_sentence(sentence):
    for mark in mark_include_sentence:
        if mark in sentence:
            return True
    return False

def combine_single_content_to_operator(lines):
    for line in lines:
        if contain_include_sentence(line):
            return
    
    return
            

