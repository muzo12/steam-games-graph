import time
import requests
import json
import threading
import random

steam_api_key = ""

with open("private_variables.txt") as var_f:
    for line in var_f.readlines():
        if line[0] == '#': continue
        if ("steam_api_key") in line:
            steam_api_key = line.partition("steam_api_key=")[2]
            steam_api_key = steam_api_key.strip("\n")
            print(steam_api_key)

users_scraped = []

files_with_users = ["wip_data\\profiles0.txt"]

def send_api_requests(profiles):
    i = 0
    for profile in profiles:
        request = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + \
                  steam_api_key + '&steamid=' + profile + '&format=json'
        response = requests.get(request)

        try:
            json_response = json.loads(response.text)
        except:
            print("error!")
            continue

        if 'games' not in json_response['response']:
            print(i, 'is private')
            i += 1
            continue

        print(i, profile, "scraping", json_response)
        user = {'time': time.time(), 'profile': profile, 'games': json_response['response']['games']}

        users_scraped.append(user)

        time.sleep(random.random() * 5 + 2)  # some random delay not to get banned, values are arbitrary

        i += 1

for file in files_with_users:
    print('starting file:', file)

    threads_num = 8
    threads = []

    profiles = []
    with open(file) as f:
        for line in f:
            if len(line) < 5: continue
            line = line.strip("\n")
            profiles.append(line)

    for i in range(threads_num):
        profiles_chunk = profiles[int(i*len(profiles)/threads_num):int((i+1)*len(profiles)/threads_num)]
        print('batch:', i, '\tlenght:', len(profiles_chunk),
              '\tfirst element:', profiles_chunk[0], '\tlast element:', profiles_chunk[len(profiles_chunk)-1])
        t = threading.Thread(target = send_api_requests, args = (profiles_chunk,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print('all threads finished')

    scraped = file.partition('.txt')[0]+'_scraped.txt'
    with open(scraped, 'w') as f:
        for user in users_scraped:
            print('writing:', user['profile'])
            f.write(json.dumps(user)+"\n")

    print('finished file:', file)