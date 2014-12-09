__author__ = 'Rick'

import os
import time


def _create_folder(container, name):
    try:
        os.listdir(container)
    except:
        os.makedirs(container)
    try:
        os.listdir(container + "\\" + name)
    except:
        os.makedirs(container + "\\" + name)
    folder_name = container + "\\\\" + name
    return folder_name


def _write_file(folder_name, file_name, string):
    total_file_dir = folder_name + "\\\\" + file_name

    total_file_path = total_file_dir + ".py"
    if os.path.exists(total_file_path):  # if succeeds the file exists
        copy = 0
        while True:
            copy += 1
            total_file_path = total_file_dir + " (%i)"%(copy)  + ".py"
            if not os.path.exists(total_file_path):
                break

    file = open(total_file_path, "w+")
    for i in string:
        file.write(str(i))
    file.close()


def saveToFile(paths, path_length, seed):
    datum = time.strftime("%d-%m-%Y")
    folder_name = _create_folder("Oplossingen Rick", datum)

    file_name = "sim" + str(path_length) + "_seed_" + str(seed)+ "_" + str(len(paths))
    to_write = "paths =", paths
    _write_file(folder_name, file_name, to_write)
