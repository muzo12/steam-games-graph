"""
This doesn't work for 80% of the games. Response is either empty, or "ValveTestApp..."... 
Let's just use Scrapy instead. >_>
"""

import json
import requests
import threading
import random
import time

steam_api_key = ""

with open("private_variables.txt") as var_f:
    for line in var_f.readlines():
        if line[0] == '#': continue
        if "steam_api_key" in line:
            steam_api_key = line.partition("steam_api_key=")[2]
            steam_api_key = steam_api_key.strip("\n")
            # print(steam_api_key)

all_games_dict = {}
keys_not_found_list = []

def send_api_requests(_appids_list):
    for id in _appids_list:
        id = id.strip('appid')
        request = 'http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key=' \
                + steam_api_key + '&appid=' + id
        response = requests.get(request)

        try:
            json_response = json.loads(response.text)
        except:
            print('error! id:', id)
            continue

        try:
            name = json_response['game']['gameName']
            if ('ValveTestApp' in name) | (name == ""):
                print("key not found for game:", id)
                keys_not_found_list.append(id)
                continue
        except KeyError:
            print("key not found for game:", id)
            keys_not_found_list.append(id)
            continue

        all_games_dict[id] = name

        print(id, name)

        time.sleep(random.random() * 2 + 1)     # random delay

threads_num = 6
threads = []
with open("wip_data\\_dataframe_merged_appids.txt") as appids_f:
    all_appids = json.loads(appids_f.read())
    print('all appids:', len(all_appids),
          '\tfirst element:', all_appids[0], '\tlast element:', all_appids[len(all_appids)-1])

for i in range(threads_num):
    appids_list = all_appids[int(i*len(all_appids)/threads_num):int((i+1)*len(all_appids)/threads_num)]
    print('batch:', i, '\tlenght:', len(appids_list),
          '\tfirst element:', appids_list[0], '\tlast element:', appids_list[len(appids_list)-1])
    t = threading.Thread(target = send_api_requests, args = (appids_list,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print('all threads finished')
with open("wip_data\\_found_appids.json", 'w') as f:
    f.write(json.dump(all_games_dict), sort_keys=True)
with open("wip_data\\_empty_appids.json", 'w') as f:
    f.write(json.dump(keys_not_found_list))
print('finished!')