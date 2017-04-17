import time
import requests
import json
import threading
import random

steam_api_key = ""

with open("private_variables.txt") as var_f:
    for line in var_f.readlines():
        if ("steam_api_key") in line:
            steam_api_key = line.partition("steam_api_key=")[0]
            steam_api_key.strip("\n")


def send_api_requests(profiles_file, output_file):
    i = 0
    with open(profiles_file) as f, open(output_file, 'w') as f_s:
        for line in f.readlines():

            line = line.strip('\n')
            request = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=' + \
                      steam_api_key + '&steamid=' + str(line) + '&format=json'
            response = requests.get(request)

            try:
                json_response = json.loads(response.text)
            except:
                print("error!")
                continue

            if 'games' not in json_response['response']:
                print('is private')
                continue

            i += 1
            print(i, line, "scraping", json_response)
            user = {'time': time.time(), 'profile': line, 'games': json_response['response']['games']}
            user_str = json.dumps(user)

            f_s.write(user_str + "\n")

            time.sleep(random.random() * 5 + 2)     # some random delay not to get banned, values are arbitrary


threads = []
for i in range(4, 12):      # here i'm specifying which profilesX.txt i want to process simultaneously.
    profiles = "profiles" + str(i) + ".txt"
    output = "profiles" + str(i) + "_scraped.txt"
    t = threading.Thread(target=send_api_requests, args=(profiles, output))
    threads.append(t)
    t.start()
