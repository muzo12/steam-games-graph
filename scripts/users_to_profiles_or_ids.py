# cleans data from steam_groups_spider.py
# splits found users into 2 categories:
# 1. users with profile numbers we can use right away
# 2. users with vanity urls we have to process

import json

max_profiles = 100000
current_profile = 0
current_profile_file = 0
max_vanityurls = 100000
current_vanityurl = 0
current_vanityurl_file = 0

with open("wip_data\\users.json") as f:
    for line in f.readlines():
        if ',\n' in line:
            l = line.replace(',\n','')
        else:
            continue
        try:
            json_line = json.loads(l)
        except:
            continue
        url = json_line['href']
        if 'http://steamcommunity.com/id/' in url:
            current_vanityurl += 1
            if current_vanityurl >= max_vanityurls:
                print("current_vanityurl_file", current_vanityurl_file)
                current_vanityurl = 0
                current_vanityurl_file += 1
            with open("wip_data\\vanity_urls"+str(current_vanityurl_file) + ".txt", 'a') as f2:
                string = url.partition("http://steamcommunity.com/id/")[2] + "\n"
                f2.write(string)
        if 'http://steamcommunity.com/profiles/' in url:
            current_profile += 1
            if current_profile >= max_vanityurls:
                print("current_profile_file", current_profile_file)
                current_profile = 0
                current_profile_file += 1
            with open("wip_data\\profiles"+str(current_profile_file)+".txt", 'a') as f2:
                string = url.partition("http://steamcommunity.com/profiles/")[2] + "\n"
                f2.write(string)