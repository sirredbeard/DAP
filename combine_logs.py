#!/usr/bin/python3

import os

LOG_DIR = "logging"
COMBINED_LOG = LOG_DIR + "/combined.log"

def get_log_files():
    logs = []
    for file in os.listdir(LOG_DIR):
        if file.endswith(".log"):
            logs.append(LOG_DIR + "/" + file)
    return logs

def read_log_file(file_str):
    file_dict = {}

    f = open(file_str, 'r')
    for line in f:
        if not line.startswith('\t'):
            # else we use the previous count, etc values
            split = line.split(' ')
            date = split[0]
            time = split[1]
            count = int(split[2].replace('[', '').replace(']', ''))

            split2 = split[3].split('\t')
            log_type = split2[0].replace(':', '')
            log_level = split2[1]
            message = ' '.join(split[4:]).replace('\n', '')
            
            file_dict[count] = {
                    "date":     date,
                    "time":     time,
                    "log_type": log_type,
                    "log_level": log_level,
                    "message": message
            }
        else:
            # If begin of new log, values have been set again, else
            # if newline just using previous values and appending to message
            message = line.replace('\t', '').replace('\n', '')
            file_dict[count]["message"] += " %s" % message
    return file_dict

def get_combined_log():
    combined_dict = {}

    for file in get_log_files():
        combined_dict.update((read_log_file(file)))

    sorted_keys = sorted(combined_dict.keys())
    sorted_dict = {}
    for key in sorted_keys:
        sorted_dict[key] = combined_dict[key]

    return sorted_dict

if __name__ == "__main__":
    combined_log = get_combined_log()

    f = open(COMBINED_LOG, 'w')
    for index in combined_log.keys():
        log_data = combined_log[index]
        line = "%s %s [%s] %s:\t%s %s" % (log_data["date"], log_data["time"], index, log_data["log_type"], log_data["log_level"], log_data["message"])
        f.write(line + '\n')
    f.close()