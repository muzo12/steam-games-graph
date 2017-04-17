import time
import requests
import json
import threading
import random

def send_api_requests(profiles_file, output_file):
    i = 0
    with open(profiles_file) as f, open(output_file, 'w') as f_s:
        for line in f.readlines():

            line = line.strip('\n')
            request = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=72F77389F14B4FB411282FF0631DBB93&steamid='+str(line)+'&format=json'
            response = requests.get(request)

            try:
                json_response = json.loads(response.text)
            except:
                print("error!")
                continue

            if 'games' not in json_response['response']:
                print('is private')
                continue

            i +=1
            print(i,line,"scraping",json_response)
            user = {}
            user['time'] = time.time()
            user['profile'] = line
            user['games'] = json_response['response']['games']

            user_str = json.dumps(user)

            f_s.write(user_str+"\n")

            time.sleep(random.random()*5+2)

threads = []
for i in range(4,12):
    profiles = "profiles"+str(i)+".txt"
    output = "profiles"+str(i)+"_scraped.txt"
    t = threading.Thread(target=send_api_requests, args=(profiles,output))
    threads.append(t)
    t.start()