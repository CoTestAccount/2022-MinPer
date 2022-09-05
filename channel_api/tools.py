import os

def pre_process_permission_file(file_name):
    permissions = open(file_name, "r").readlines()
    for line in permissions:
        line = line.replace("\n", "")
        tks = line.split()
        if len(tks) < 3:
            continue
        