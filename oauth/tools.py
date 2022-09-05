from curses.ascii import isalpha
import os



ifttt_header_sentence = []

stop_words = ["agree", "cancel", "authorize", "approve", 
    "deny", "accept", "decline", "continue",
    "allow", "allowdeny", "logout",
    "more", "no", "ok", "okay",
    "signout", "submit", "yes",
]
auth_folder = "/Users/***/Documents/Code/overclaim_tap/oauth/fetch_OAuth_info/modified_auth_log/"

def load_ifttt_info():
    f = "tmp.txt"
    lines = open(f, "r").readlines()
    ifttt_header_sentence.extend(lines)


def format_lines(lines):
    return [x.lower() for x in lines]


def output_(lines):
    print(''.join(lines))

def print_information_followed_ifttt_header(file):
    file_path = auth_folder + file
    lines = format_lines(open(file_path, "r"))

    mark = -1
    for index, line in enumerate(lines):
        if line in ifttt_header_sentence:
            mark = index
    if mark == -1:
        return
    print("#################################### ", file)
    output_(lines[mark:])


def remove_non_alpha_space(str):
    new_str = ''
    for s in str:
        if isalpha(s):
            new_str += s
        if s == ' ':
            new_str += s
    return new_str

def filter_lines_followed_agree(sentences):
    lines = format_lines(sentences)
    mark = -1
    for index, line in enumerate(lines):
        text = remove_non_alpha_space(line)
        if text == '':
            continue
        tks = text.split(' ')
        if text in stop_words:
            mark = index
            break
        
        contains_other_words = False
        for tk in tks:
            if tk not in stop_words:
                contains_other_words = True

        if contains_other_words == False:
            mark = index
    if mark == -1:
        return sentences
    
    return(sentences[:mark])


if __name__ == "__main__":
    files = os.listdir(auth_folder)

    load_ifttt_info()
    for file in files:
        if "_phase1" in file:
            continue
        print_information_followed_agree(file)