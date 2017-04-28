import json
import time

appids_list = json.loads(open("wip_data\\_dataframe_merged_appids.txt", 'r').read())

print(appids_list)

with open("wip_data\\_appids_scrapped.json", 'r') as f:
    for line in f:
        if len(line)<10: continue
        line = line.replace(",\n","")

        line_json = json.loads(line)
        appid = "appid"+str(line_json['appid'])

        try:
            appids_list.remove(appid)
        except ValueError:
            print("appid not in list:",appid)
            time.sleep(1)
            continue

with open("wip_data\\_ghost_appids.txt", 'w') as f:
    f.write(json.dumps(appids_list))